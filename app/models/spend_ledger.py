"""One recorded provider call, priced in the operator's currency."""

from datetime import datetime

from pydantic import BaseModel, Field


class SpendLedgerEntry(BaseModel):
    """What one completed provider call cost, and when.

    Entries are written one per call and never updated. The total for a period
    is their sum, which is why concurrent calls cannot lose each other's cost
    the way a single running total read, incremented and written back would.
    """

    entry_id: str
    recorded_at: datetime
    # The calendar month this counts against, as YYYY-MM in UTC. Stored rather
    # than derived at read time so an entry keeps counting against the month it
    # was actually spent in, whatever the reader's clock says later.
    period: str = Field(pattern=r"^\d{4}-\d{2}$")
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cost: float = Field(ge=0)
    currency: str


class SpendLedgerState(BaseModel):
    """What the ledger currently reports, for the console and /api/status."""

    enforced: bool
    currency: str
    period: str
    ceiling: float | None = None
    spent: float
    remaining: float | None = None
    calls: int = Field(ge=0)
    # True when a ceiling is configured but the prices needed to honour it are
    # not, which is the state where paid endpoints refuse rather than serve.
    misconfigured: bool = False
