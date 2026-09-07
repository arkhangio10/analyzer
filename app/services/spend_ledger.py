"""Stop the application spending past a ceiling the operator set.

A cloud budget does not do this. It sends mail when a threshold is crossed and
the spending continues, which is useful for noticing and useless for stopping.
The only thing that can refuse the next call is the code about to make it, so
the ceiling lives here.

Every provider call is priced from the tokens the provider reports and written
as its own entry. A period's spend is the sum of its entries. That shape is
chosen for a reason: a single running total would have to be read, incremented
and written back, and two containers doing that at once lose one of the two
costs. Entries cannot lose each other.

What this is not: it is not exact, and it is not a hard guarantee. The check
happens before a call and the cost is known only after it, so calls already in
flight when the ceiling is reached still complete and still count. With a small
number of concurrent callers the overshoot is one call's cost, not a bill. A
provider call that fails is not priced, because no usage is reported for it.

If a ceiling is set and the prices needed to honour it are not, the paid
endpoints refuse rather than serve. A ceiling that cannot be computed is worse
than no ceiling: it reads as protection while providing none.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import Settings, get_settings
from app.models.spend_ledger import SpendLedgerEntry, SpendLedgerState
from app.models.video_extraction import GeminiUsage
from app.services.record_store import RecordStore


logger = logging.getLogger(__name__)


class SpendCeilingReached(RuntimeError):
    """Raised instead of making a call that would spend past the ceiling."""

    def __init__(self, state: SpendLedgerState) -> None:
        super().__init__(
            f"This deployment has spent {state.spent:.2f} {state.currency} of its "
            f"{state.ceiling:.2f} {state.currency} ceiling for {state.period}. "
            "No further provider calls will be made until the ceiling is raised "
            "or the period rolls over."
        )
        self.state = state


class SpendLedgerNotConfigured(RuntimeError):
    """Raised when a ceiling is set but its prices are not."""


def current_period(now: datetime | None = None) -> str:
    """Return the calendar month, in UTC, that spending counts against."""
    moment = now or datetime.now(timezone.utc)
    return f"{moment.year:04d}-{moment.month:02d}"


class SpendLedger:
    """Price provider calls, total them, and refuse to pass the ceiling."""

    def __init__(
        self,
        store: RecordStore,
        settings: Settings | None = None,
    ) -> None:
        self._store = store
        self._settings = settings or get_settings()

    # --- configuration -----------------------------------------------------

    @property
    def currency(self) -> str:
        return self._settings.spend_currency

    @property
    def ceiling(self) -> float | None:
        return self._settings.spend_ceiling

    @property
    def can_price(self) -> bool:
        """Report whether a call's cost can be computed at all."""
        return (
            self._settings.price_per_million_input_tokens is not None
            and self._settings.price_per_million_output_tokens is not None
        )

    @property
    def is_enforced(self) -> bool:
        """Report whether a call can actually be refused for cost."""
        return self.ceiling is not None and self.can_price

    @property
    def is_misconfigured(self) -> bool:
        """Report a ceiling that cannot be honoured because prices are absent."""
        return self.ceiling is not None and not self.can_price

    # --- pricing -----------------------------------------------------------

    def price(self, usage: GeminiUsage) -> float:
        """Return what one call cost, from the tokens the provider reported.

        Cached input is billed at a lower rate by most providers, and no
        attempt is made to model that here: counting it at the full input rate
        overstates the cost slightly, which is the safe direction for a
        ceiling to be wrong in.
        """
        if not self.can_price:
            raise SpendLedgerNotConfigured(
                "PRICE_PER_MILLION_INPUT_TOKENS and "
                "PRICE_PER_MILLION_OUTPUT_TOKENS must both be set before a "
                "call can be priced."
            )
        input_tokens = usage.prompt_tokens or 0
        output_tokens = (usage.candidate_tokens or 0) + (usage.thoughts_tokens or 0)
        input_rate = self._settings.price_per_million_input_tokens or 0.0
        output_rate = self._settings.price_per_million_output_tokens or 0.0
        return (
            input_tokens * input_rate + output_tokens * output_rate
        ) / 1_000_000

    # --- reading -----------------------------------------------------------

    def entries(self, period: str | None = None) -> list[SpendLedgerEntry]:
        """Return the entries counting against one period, oldest first."""
        wanted = period or current_period()
        stored = self._store.load_all(SpendLedgerEntry).values()
        return sorted(
            (entry for entry in stored if entry.period == wanted),
            key=lambda entry: entry.recorded_at,
        )

    def state(self, period: str | None = None) -> SpendLedgerState:
        """Report the ledger as the console and /api/status show it."""
        wanted = period or current_period()
        entries = self.entries(wanted)
        spent = round(sum(entry.cost for entry in entries), 6)
        ceiling = self.ceiling
        return SpendLedgerState(
            enforced=self.is_enforced,
            currency=self.currency,
            period=wanted,
            ceiling=ceiling,
            spent=spent,
            remaining=None if ceiling is None else round(max(ceiling - spent, 0.0), 6),
            calls=len(entries),
            misconfigured=self.is_misconfigured,
        )

    # --- the two things callers do -----------------------------------------

    def check(self) -> None:
        """Refuse the call that is about to be made, if it would pass the ceiling."""
        if self.is_misconfigured:
            raise SpendLedgerNotConfigured(
                f"SPEND_CEILING is set to {self.ceiling} {self.currency} but "
                "PRICE_PER_MILLION_INPUT_TOKENS and "
                "PRICE_PER_MILLION_OUTPUT_TOKENS are not, so spending cannot "
                "be measured against it. Set both prices, or unset the ceiling."
            )
        if not self.is_enforced:
            return
        state = self.state()
        if state.spent >= (state.ceiling or 0.0):
            raise SpendCeilingReached(state)

    def record(self, model: str, usage: GeminiUsage) -> SpendLedgerEntry | None:
        """Write what one completed call cost. Returns None if it cannot be priced.

        A failure to write is logged and swallowed: losing the record of a call
        that already happened must not also fail the request that produced the
        evidence. The consequence is honest and worth stating -- an unwritable
        ledger under-counts, so `records_survive_restart` being false makes the
        ceiling advisory rather than real.
        """
        if not self.can_price:
            return None
        now = datetime.now(timezone.utc)
        entry = SpendLedgerEntry(
            entry_id=f"spend{uuid4().hex[:16]}",
            recorded_at=now,
            period=current_period(now),
            model=model,
            input_tokens=usage.prompt_tokens or 0,
            output_tokens=(usage.candidate_tokens or 0)
            + (usage.thoughts_tokens or 0),
            cost=round(self.price(usage), 6),
            currency=self.currency,
        )
        if not self._store.save(entry.entry_id, entry):
            logger.error(
                "A provider call costing %.6f %s could not be written to the "
                "spend ledger. The ceiling is now under-counting.",
                entry.cost,
                entry.currency,
            )
        return entry
