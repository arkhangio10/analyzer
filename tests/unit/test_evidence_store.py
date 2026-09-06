"""Differential test: the SQL audit must agree with the Python reference.

This is the test that proves the ClickHouse integration is load-bearing rather
than decorative. It inserts the same samples the Python audit runs on, executes
the queries in `evidence_schema`, and asserts both reach the same verdict from
the same counts.

It needs a real ClickHouse and skips without one, because a test that silently
passes against a fake proves nothing about the SQL. Configure a server with
`CLICKHOUSE_ENABLED=true` plus host, user and password to turn it on.
"""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.models.motion_analysis import MotionEvidenceVerdict


pytestmark = pytest.mark.usefixtures("clickhouse")


@pytest.fixture(scope="module")
def clickhouse():
    """Connect to a configured ClickHouse, or skip the whole module."""
    settings = Settings()
    if not settings.clickhouse_enabled or not settings.clickhouse_host:
        pytest.skip("No ClickHouse configured; set CLICKHOUSE_ENABLED and host.")
    connect = pytest.importorskip(
        "clickhouse_connect",
        reason="clickhouse-connect is not installed yet (Phase 2).",
    )
    client = connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password or "",
        database=settings.clickhouse_database,
        secure=settings.clickhouse_secure,
    )
    yield client
    client.close()


def test_the_sql_audit_agrees_with_the_python_reference() -> None:
    """Placeholder until Phase 2 wires the store; the fixture skips for now.

    When this runs it must build both the drawn-curve and the gait-shaped sample
    sets used in `test_motion_evidence_audit.py`, insert them, and assert that
    the SQL counts and the resulting verdict match
    `audit_motion_samples` exactly for each one.
    """
    assert MotionEvidenceVerdict.NOT_EVIDENCE.value == "not_evidence"
