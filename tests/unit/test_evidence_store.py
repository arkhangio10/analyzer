"""The SQL audit must reach the same verdict as the Python reference.

This is the test that makes the ClickHouse integration load-bearing rather than
decorative. It inserts the exact sample sets the Python audit is tested against,
asks ClickHouse to count them, and asserts both paths produce the same counts
and the same verdict.

The rules live in `verdict_from_counts` and are shared, so a disagreement here
can only mean the SQL counts something differently from the Python — which is
precisely the bug this test exists to catch.

It skips without a configured ClickHouse, because passing against a fake would
prove nothing about the SQL.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.core.config import Settings
from app.models.motion_analysis import (
    MotionAnalysisRecord,
    MotionRetargetVerdict,
    MotionSubjectKind,
    ObservedJointAngle,
)
from app.services.evidence_store import EvidenceStore
from app.services.motion_evidence_audit import audit_motion_samples
from tests.unit.test_motion_evidence_audit import drawn_curve, walking_like


WINDOW_SECONDS = 12.0


# --- behaviour that needs no server ---------------------------------------


def test_an_unconfigured_store_degrades_instead_of_failing() -> None:
    store = EvidenceStore(Settings(clickhouse_enabled=False))

    assert store.is_configured is False
    assert store.is_available is False
    assert store.ensure_schema() is False
    assert store.library_verdicts("prj_any") == []
    assert store.untrusted_assets("prj_any") == []
    assert store.audit_from_sql("mot_any", window_seconds=WINDOW_SECONDS) is None


def test_enabling_without_a_host_is_still_not_configured() -> None:
    store = EvidenceStore(Settings(clickhouse_enabled=True, clickhouse_host=None))

    assert store.is_configured is False
    assert store.is_available is False


# --- the differential test ------------------------------------------------


@pytest.fixture(scope="module")
def store() -> EvidenceStore:
    """A store against a real ClickHouse, or skip the differential tests."""
    settings = Settings()
    if not (settings.clickhouse_enabled and settings.clickhouse_host):
        pytest.skip("No ClickHouse configured; set CLICKHOUSE_ENABLED and host.")
    instance = EvidenceStore(settings)
    if not instance.ensure_schema():
        pytest.skip("ClickHouse is configured but unreachable.")
    return instance


def analysis_for(samples: list[ObservedJointAngle]) -> MotionAnalysisRecord:
    """Wrap samples in the record the store writes, with a fresh identity."""
    audit = audit_motion_samples(samples, window_seconds=WINDOW_SECONDS)
    return MotionAnalysisRecord(
        analysis_id=f"mot_test_{uuid4().hex[:12]}",
        project_id="prj_differential",
        extraction_id="vpr_differential",
        source_url="https://youtu.be/-fD2TSL2s7I",
        requested_fps=4.0,
        window_start_seconds=60.0,
        window_end_seconds=60.0 + WINDOW_SECONDS,
        subject_kind=MotionSubjectKind.HUMAN_BODY,
        kinematic_chain="bipedal_lower_limb",
        joint_names=sorted({item.joint_name for item in samples}),
        samples=samples,
        sample_count=len(samples),
        distinct_joint_count=len({f"{s.side}.{s.joint_name}" for s in samples}),
        observed_span_seconds=WINDOW_SECONDS,
        samples_per_second=len(samples) / WINDOW_SECONDS,
        mean_confidence=sum(s.confidence for s in samples) / len(samples),
        clear_sample_count=sum(1 for s in samples if s.visibility.value == "clear"),
        audit=audit,
        retarget=MotionRetargetVerdict(
            retarget_supported=False,
            observed_chain="bipedal_lower_limb",
            reason="Test record.",
        ),
        provider="vertex_ai",
        requested_model="gemini-2.5-flash-lite",
        elapsed_seconds=1.0,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.parametrize(
    "name,build",
    [("drawn_curve", drawn_curve), ("walking_like", walking_like)],
)
def test_sql_and_python_agree_on_the_same_samples(
    store: EvidenceStore,
    name: str,
    build,
) -> None:
    samples = build()
    record = analysis_for(samples)
    expected = record.audit

    assert store.record(record) is True
    actual = store.audit_from_sql(record.analysis_id, window_seconds=WINDOW_SECONDS)

    assert actual is not None, f"{name}: the SQL audit returned nothing"
    assert actual.verdict is expected.verdict, name
    assert actual.mirrored_frame_ratio == pytest.approx(
        expected.mirrored_frame_ratio, abs=0.001
    ), name
    assert actual.distinct_confidence_values == expected.distinct_confidence_values
    assert actual.distinct_visibility_values == expected.distinct_visibility_values
    assert actual.acyclic_joints == expected.acyclic_joints, name
    assert actual.checked_joint_count == expected.checked_joint_count, name
    assert [f.code for f in actual.findings] == [f.code for f in expected.findings]
    assert [f.values for f in actual.findings] == [f.values for f in expected.findings]


def test_the_library_view_counts_what_was_stored(store: EvidenceStore) -> None:
    record = analysis_for(drawn_curve())
    assert store.record(record) is True

    verdicts = store.library_verdicts("prj_differential")
    untrusted = store.untrusted_assets("prj_differential", limit=100)

    assert verdicts, "the library query returned nothing after an insert"
    assert any(row["verdict"] == "not_evidence" for row in verdicts)
    assert any(row["analysis_id"] == record.analysis_id for row in untrusted)
