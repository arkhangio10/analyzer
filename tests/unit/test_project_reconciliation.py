"""Tests for reconciling a project's approved procedures."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.runtime import project_video_procedure_service
from app.main import app
from app.models.procedure import Procedure, ProcedureStep
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)
from app.services.project_reconciliation_service import (
    NotEnoughApprovedSourcesError,
    ProjectReconciliationService,
)


client = TestClient(app)
BASE = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
FIRST_SOURCE = "https://youtu.be/-fD2TSL2s7I"
SECOND_SOURCE = "https://youtu.be/second-source"


def record(
    extraction_id: str,
    actions: list[str],
    *,
    project_id: str = "prj_reconcile01",
    source_url: str = FIRST_SOURCE,
    status: ProjectVideoProcedureStatus = ProjectVideoProcedureStatus.APPROVED,
    version: int = 1,
    minutes: int = 0,
    rules: list[str] | None = None,
) -> ProjectVideoProcedureRecord:
    return ProjectVideoProcedureRecord(
        extraction_id=extraction_id,
        project_id=project_id,
        procedure_version=version,
        source_url=source_url,
        status=status,
        procedure=Procedure(
            task="Walk",
            objective="Demonstrate walking mechanics.",
            steps=[
                ProcedureStep(step=index + 1, action=action)
                for index, action in enumerate(actions)
            ],
            rules=rules or [],
        ),
        created_at=BASE + timedelta(minutes=minutes),
    )


def service() -> ProjectReconciliationService:
    return ProjectReconciliationService()


def test_one_approved_procedure_cannot_be_reconciled() -> None:
    with pytest.raises(NotEnoughApprovedSourcesError) as error:
        service().reconcile(
            "prj_reconcile01",
            [record("vpr_a", ["Push off with the hips."])],
            "Walk",
        )

    assert "has 1" in str(error.value)


def test_unapproved_procedures_are_never_counted() -> None:
    with pytest.raises(NotEnoughApprovedSourcesError):
        service().reconcile(
            "prj_reconcile01",
            [
                record("vpr_a", ["One."]),
                record(
                    "vpr_b",
                    ["One."],
                    status=ProjectVideoProcedureStatus.AWAITING_REVIEW,
                    minutes=5,
                ),
                record(
                    "vpr_c",
                    ["One."],
                    status=ProjectVideoProcedureStatus.REJECTED,
                    minutes=6,
                ),
            ],
            "Walk",
        )


def test_two_readings_of_one_video_are_not_independent_confirmation() -> None:
    reconciliation = service().reconcile(
        "prj_reconcile01",
        [
            record("vpr_a", ["Push off with the hips."], version=1),
            record("vpr_b", ["Push off with the hips."], version=2, minutes=5),
        ],
        "Walk",
    )

    assert reconciliation.distinct_source_count == 1
    assert reconciliation.is_cross_source is False
    assert "repeating itself" in reconciliation.independence_note
    assert reconciliation.result.confidence == 1.0
    assert reconciliation.result.conflicts == []


def test_two_different_videos_count_as_cross_source() -> None:
    reconciliation = service().reconcile(
        "prj_reconcile01",
        [
            record("vpr_a", ["Push off with the hips."]),
            record(
                "vpr_b",
                ["Push off with the hips."],
                source_url=SECOND_SOURCE,
                minutes=5,
            ),
        ],
        "Walk",
    )

    assert reconciliation.distinct_source_count == 2
    assert reconciliation.is_cross_source is True
    assert "evidence about the task" in reconciliation.independence_note


def test_a_contradiction_between_sources_is_surfaced_not_resolved() -> None:
    reconciliation = service().reconcile(
        "prj_reconcile01",
        [
            record("vpr_a", ["Push off with the hips."]),
            record(
                "vpr_b",
                ["Drive the knee forward."],
                source_url=SECOND_SOURCE,
                minutes=5,
            ),
        ],
        "Walk",
    )

    assert reconciliation.result.conflicts
    assert "competing actions" in reconciliation.result.conflicts[0]
    assert reconciliation.result.ready_for_practice is False


def test_every_source_that_fed_the_result_is_named() -> None:
    reconciliation = service().reconcile(
        "prj_reconcile01",
        [
            record("vpr_a", ["One.", "Two."], version=1),
            record(
                "vpr_b",
                ["One."],
                source_url=SECOND_SOURCE,
                version=2,
                minutes=5,
            ),
        ],
        "Walk",
    )

    assert [item.extraction_id for item in reconciliation.sources] == ["vpr_a", "vpr_b"]
    assert [item.step_count for item in reconciliation.sources] == [2, 1]
    assert reconciliation.sources[1].source_url == SECOND_SOURCE
    assert reconciliation.result.uncertainties


def test_the_endpoint_refuses_and_then_reports_once_two_are_approved() -> None:
    project = client.post(
        "/api/projects",
        json={
            "task_description": "Learn the walking mechanics demonstrated in the video.",
            "destination": "robot",
            "language": "en",
            "robot_model": "APRENDIZ SimArm-6",
        },
    ).json()
    project_id = project["project_id"]
    url = f"/api/projects/{project_id}/video-procedures/history/reconciliation"

    first = record("vpr_rec_one", ["One."], project_id=project_id)
    project_video_procedure_service._records[first.extraction_id] = first
    too_few = client.get(url)

    second = record(
        "vpr_rec_two",
        ["One."],
        project_id=project_id,
        source_url=SECOND_SOURCE,
        version=2,
        minutes=5,
    )
    project_video_procedure_service._records[second.extraction_id] = second
    ready = client.get(url)

    assert too_few.status_code == 409
    assert "has 1" in too_few.json()["detail"]
    assert ready.status_code == 200
    body = ready.json()
    assert body["is_cross_source"] is True
    assert body["distinct_source_count"] == 2
    assert len(body["sources"]) == 2
    assert body["result"]["source_count"] == 2
