"""Tests for the ceiling the application enforces on its own spending.

A cloud budget notifies and the spending continues. This ledger refuses, so
these tests hold the properties that make refusing trustworthy:

- a call is priced from reported tokens, and entries accumulate;
- the ceiling actually stops the next call, through the real service boundary;
- a ceiling that cannot be priced refuses rather than serving unprotected,
  which is the same choice the spend token guard makes for the same reason;
- entries count against the period they were spent in, not the reader's.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.spend_guard import SPEND_TOKEN_HEADER
from app.core.config import Settings
from app.main import app
from app.models.spend_ledger import SpendLedgerEntry
from app.models.video_extraction import GeminiUsage, VideoExtractionRequest
from app.services.gemini_service import GeminiService
from app.services.record_store import JsonRecordStore
from app.services.spend_ledger import (
    SpendCeilingReached,
    SpendLedger,
    SpendLedgerNotConfigured,
    current_period,
)


PRICED = {
    "spend_currency": "PEN",
    "price_per_million_input_tokens": 1.0,
    "price_per_million_output_tokens": 4.0,
}


@pytest.fixture
def store(tmp_path):
    return JsonRecordStore(tmp_path / "spend-ledger")


def ledger(store, **overrides) -> SpendLedger:
    return SpendLedger(store=store, settings=Settings(**overrides))


# --- pricing ---------------------------------------------------------------


def test_a_call_is_priced_from_the_tokens_the_provider_reported(store) -> None:
    book = ledger(store, **PRICED)

    cost = book.price(
        GeminiUsage(prompt_tokens=1_000_000, candidate_tokens=500_000)
    )

    assert cost == pytest.approx(1.0 + 2.0)


def test_thinking_tokens_are_billed_as_output(store) -> None:
    """They are output the provider charges for; leaving them out under-counts."""
    book = ledger(store, **PRICED)

    with_thoughts = book.price(
        GeminiUsage(prompt_tokens=0, candidate_tokens=0, thoughts_tokens=1_000_000)
    )

    assert with_thoughts == pytest.approx(4.0)


def test_pricing_without_configured_prices_refuses_rather_than_guessing(store) -> None:
    with pytest.raises(SpendLedgerNotConfigured):
        ledger(store).price(GeminiUsage(prompt_tokens=10))


# --- accumulating ----------------------------------------------------------


def test_recorded_calls_accumulate(store) -> None:
    book = ledger(store, spend_ceiling=20.0, **PRICED)

    book.record("gemini-2.5-flash-lite", GeminiUsage(prompt_tokens=1_000_000))
    book.record("gemini-2.5-flash-lite", GeminiUsage(prompt_tokens=2_000_000))

    state = book.state()
    assert state.calls == 2
    assert state.spent == pytest.approx(3.0)
    assert state.remaining == pytest.approx(17.0)


def test_each_call_is_its_own_entry(store) -> None:
    """Entries cannot lose each other; a shared running total could."""
    book = ledger(store, **PRICED)

    book.record("m", GeminiUsage(prompt_tokens=1))
    book.record("m", GeminiUsage(prompt_tokens=1))

    assert len(store.load_all(SpendLedgerEntry)) == 2


def test_spending_counts_against_the_period_it_was_spent_in(store) -> None:
    book = ledger(store, spend_ceiling=20.0, **PRICED)
    store.save(
        "spendold",
        SpendLedgerEntry(
            entry_id="spendold",
            recorded_at=datetime(2020, 1, 5, tzinfo=timezone.utc),
            period="2020-01",
            model="m",
            input_tokens=20_000_000,
            output_tokens=0,
            cost=20.0,
            currency="PEN",
        ),
    )

    assert book.state().spent == 0.0
    assert book.state("2020-01").spent == pytest.approx(20.0)


def test_the_period_is_the_utc_calendar_month() -> None:
    assert current_period(datetime(2026, 9, 7, tzinfo=timezone.utc)) == "2026-09"


# --- refusing --------------------------------------------------------------


def test_no_ceiling_means_nothing_is_refused(store) -> None:
    book = ledger(store, **PRICED)
    book.record("m", GeminiUsage(prompt_tokens=999_000_000))

    book.check()

    assert book.is_enforced is False


def test_the_ceiling_refuses_the_next_call(store) -> None:
    book = ledger(store, spend_ceiling=20.0, **PRICED)
    book.record("m", GeminiUsage(prompt_tokens=20_000_000))

    with pytest.raises(SpendCeilingReached) as raised:
        book.check()

    assert raised.value.state.spent == pytest.approx(20.0)
    assert "20.00 PEN" in str(raised.value)


def test_below_the_ceiling_is_allowed(store) -> None:
    book = ledger(store, spend_ceiling=20.0, **PRICED)
    book.record("m", GeminiUsage(prompt_tokens=19_000_000))

    book.check()


def test_a_ceiling_without_prices_refuses_rather_than_serving_unprotected(
    store,
) -> None:
    """The same choice the token guard makes: an unenforceable guard is worse than none."""
    book = ledger(store, spend_ceiling=20.0)

    assert book.is_misconfigured is True
    assert book.is_enforced is False
    with pytest.raises(SpendLedgerNotConfigured):
        book.check()


# --- through the real service boundary -------------------------------------


class _StubClient:
    """Stands in for the provider so no test can make a real call."""

    def __init__(self, *args, **kwargs) -> None:
        raise AssertionError(
            "The ceiling must refuse before a client is ever created."
        )


def _extract(service: GeminiService):
    return asyncio.run(
        service.extract_procedure(
            VideoExtractionRequest(
                video_url="https://www.youtube.com/watch?v=abcdefghijk",
                task_hint="anything",
                acknowledge_cloud_cost=True,
            )
        )
    )


def test_the_service_refuses_before_reaching_the_provider(store) -> None:
    book = ledger(store, spend_ceiling=20.0, **PRICED)
    book.record("m", GeminiUsage(prompt_tokens=20_000_000))
    service = GeminiService(
        settings=Settings(google_genai_enabled=True, **PRICED),
        client_factory=_StubClient,
        ledger=book,
    )

    with pytest.raises(SpendCeilingReached):
        _extract(service)


def test_below_the_ceiling_the_service_does_reach_the_provider(store) -> None:
    """Guards the test above: it must fail for the ceiling, not for the stub."""
    book = ledger(store, spend_ceiling=20.0, **PRICED)
    service = GeminiService(
        settings=Settings(google_genai_enabled=True, **PRICED),
        client_factory=_StubClient,
        ledger=book,
    )

    with pytest.raises(AssertionError, match="before a client is ever created"):
        _extract(service)


# --- what the console is told ----------------------------------------------


def test_status_reports_the_ceiling_and_what_is_left() -> None:
    body = TestClient(app).get("/api/status").json()

    assert set(body["spend"]) >= {
        "enforced",
        "currency",
        "period",
        "ceiling",
        "spent",
        "remaining",
        "calls",
        "misconfigured",
    }


def test_a_reached_ceiling_comes_back_as_402_through_the_api(
    monkeypatch,
    store,
) -> None:
    """The handler is on the app, so no route can spend by forgetting to catch."""
    from app.api import runtime, spend_guard

    book = ledger(store, spend_ceiling=20.0, **PRICED)
    book.record("m", GeminiUsage(prompt_tokens=20_000_000))
    monkeypatch.setattr(runtime.gemini_service, "_ledger", book)
    monkeypatch.setattr(
        spend_guard,
        "get_settings",
        lambda: Settings(google_genai_enabled=True, spend_token="s3cret"),
    )

    response = TestClient(app, raise_server_exceptions=False).post(
        "/api/experiments/video/extract",
        json={
            "video_url": "https://www.youtube.com/watch?v=abcdefghijk",
            "task_hint": "anything",
            "acknowledge_cloud_cost": True,
        },
        headers={SPEND_TOKEN_HEADER: "s3cret"},
    )

    assert response.status_code == 402
    body = response.json()
    assert body["spend"]["spent"] == pytest.approx(20.0)
    assert body["spend"]["remaining"] == pytest.approx(0.0)
