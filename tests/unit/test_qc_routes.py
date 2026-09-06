"""Tests for the QC console's routes.

The console's whole value is that it does not overstate. Two of its ways of
overstating are tested here specifically:

- an empty library must not read as a clean library. When ClickHouse is absent
  the response says so and still lists what the local store holds, rather than
  returning an empty table with no explanation;
- the detail view must carry the counts, not only the verdict, because the
  claim is that the verdict is recomputable and a reader cannot check a verdict.

`prove` is asserted to spend nothing, which is what makes it safe to put behind
a button a person can press repeatedly.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api import runtime
from app.main import app
from app.models.motion_analysis import (
    MotionAnalysisRecord,
    MotionEvidenceVerdict,
    MotionRetargetVerdict,
    MotionSubjectKind,
)
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)
from app.services.motion_evidence_audit import audit_motion_samples
from tests.unit.test_motion_evidence_audit import drawn_curve, walking_like


client = TestClient(app)
WINDOW_SECONDS = 12.0


def create_project() -> str:
    response = client.post(
        "/api/projects",
        json={
            "task_description": "Learn the walking mechanics demonstrated in the video.",
            "destination": "robot",
            "language": "en",
            "robot_model": "APRENDIZ SimArm-6",
            "robot_class": "humanoid",
        },
    )
    assert response.status_code == 201
    return response.json()["project_id"]


def seed(project_id: str, samples=None, approved: bool = True) -> tuple[str, str]:
    """Put one extraction and one analysis into the running services."""
    samples = samples if samples is not None else drawn_curve()
    extraction_id = f"vpr_{uuid4().hex[:12]}"
    status = (
        ProjectVideoProcedureStatus.APPROVED
        if approved
        else ProjectVideoProcedureStatus.AWAITING_REVIEW
    )
    extraction = ProjectVideoProcedureRecord(
        extraction_id=extraction_id,
        project_id=project_id,
        source_url="https://youtu.be/-fD2TSL2s7I",
        status=status,
        provider="vertex_ai",
        requested_model="gemini-2.5-flash-lite",
        cloud_calls_made=1,
        created_at=datetime.now(timezone.utc),
    )
    runtime.project_video_procedure_service._records[extraction_id] = extraction

    analysis_id = f"mot_{uuid4().hex[:12]}"
    audit = audit_motion_samples(samples, window_seconds=WINDOW_SECONDS)
    analysis = MotionAnalysisRecord(
        analysis_id=analysis_id,
        project_id=project_id,
        extraction_id=extraction_id,
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
    runtime.motion_analysis_service._records[analysis_id] = analysis
    return extraction_id, analysis_id


# --- the console itself -----------------------------------------------------


def test_the_console_is_served_and_is_not_the_product_surface() -> None:
    page = client.get("/qc")

    assert page.status_code == 200
    body = page.text
    assert "/static/qc.js" in body
    assert "Which AI-generated metadata was actually observed?" in body
    # The robot track and the bilingual toggle belong to the other surface.
    assert "robot" not in body.casefold()
    assert "espa" not in body.casefold()


# --- the library ------------------------------------------------------------


def test_an_unknown_project_is_not_found() -> None:
    assert client.get("/api/qc/projects/prj_missing/library").status_code == 404


def test_a_library_without_clickhouse_says_so_rather_than_looking_clean() -> None:
    project_id = create_project()
    seed(project_id)

    body = client.get(f"/api/qc/projects/{project_id}/library").json()

    if body["evidence_available"]:
        pytest.skip("ClickHouse is configured; this asserts the degraded path.")
    assert "not configured or not reachable" in body["evidence_note"]
    assert body["verdicts"] == []
    assert len(body["analyses"]) == 1, "the local record store was not listed"


def test_the_library_lists_what_the_local_store_holds() -> None:
    project_id = create_project()
    _, analysis_id = seed(project_id)

    body = client.get(f"/api/qc/projects/{project_id}/library").json()

    listed = [item["analysis_id"] for item in body["analyses"]]
    assert analysis_id in listed
    assert body["evidence_note"]


# --- the detail view --------------------------------------------------------


def test_the_detail_view_carries_the_counts_not_only_the_verdict() -> None:
    project_id = create_project()
    _, analysis_id = seed(project_id, drawn_curve())

    body = client.get(
        f"/api/qc/projects/{project_id}/analyses/{analysis_id}"
    ).json()

    assert body["verdict"] == MotionEvidenceVerdict.NOT_EVIDENCE.value
    for count in (
        "mirrored_frame_ratio",
        "distinct_confidence_values",
        "distinct_visibility_values",
        "checked_joint_count",
        "sample_count",
    ):
        assert count in body, count
    assert body["findings"], "a not_evidence verdict with no findings explains nothing"
    assert body["series"], "no samples to plot means the reader cannot check anything"
    assert body["cloud_calls_made"] >= 0


def test_an_analysis_from_another_project_is_not_readable() -> None:
    owner = create_project()
    other = create_project()
    _, analysis_id = seed(owner)

    response = client.get(f"/api/qc/projects/{other}/analyses/{analysis_id}")

    assert response.status_code == 404


def test_an_unknown_analysis_is_not_found() -> None:
    project_id = create_project()

    response = client.get(f"/api/qc/projects/{project_id}/analyses/mot_absent")

    assert response.status_code == 404


# --- prove it ---------------------------------------------------------------


def test_proving_an_approved_asset_recomputes_and_agrees() -> None:
    project_id = create_project()
    extraction_id, _ = seed(project_id, walking_like())

    body = client.post(
        f"/api/qc/projects/{project_id}/extractions/{extraction_id}/prove"
    ).json()

    assert body["approved"] is True
    assert body["proven"] is True
    assert body["claimed_verdict"] == body["recomputed_verdict"]
    assert body["cloud_calls_made"] == 0


def test_proving_stops_at_the_gate_when_nobody_approved() -> None:
    project_id = create_project()
    extraction_id, _ = seed(project_id, walking_like(), approved=False)

    body = client.post(
        f"/api/qc/projects/{project_id}/extractions/{extraction_id}/prove"
    ).json()

    assert body["approved"] is False
    assert body["proven"] is False
    stages = {stage["stage"]: stage["outcome"] for stage in body["stages"]}
    assert stages["approval_gate"] == "blocked_awaiting_approval"
    assert "audit" not in stages, "a gated stage ran without approval"


def test_proving_costs_nothing_however_often_it_is_pressed() -> None:
    project_id = create_project()
    extraction_id, _ = seed(project_id, walking_like())

    for _ in range(3):
        body = client.post(
            f"/api/qc/projects/{project_id}/extractions/{extraction_id}/prove"
        ).json()
        assert body["cloud_calls_made"] == 0
        assert all(stage["cloud_calls_made"] == 0 for stage in body["stages"])
