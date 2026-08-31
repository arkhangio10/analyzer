"""Tests for procedure version history and the diff between two versions."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.api.runtime import project_video_procedure_service
from app.main import app
from app.models.procedure import Procedure, ProcedureStep
from app.models.procedure_history import StepChangeKind
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)
from app.models.video_extraction import GeminiUsage
from app.services.procedure_history_service import build_history, diff_versions


client = TestClient(app)
BASE = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)


def record(
    extraction_id: str,
    version: int,
    actions: list[str],
    *,
    project_id: str = "prj_history01",
    source_url: str = "https://youtu.be/-fD2TSL2s7I",
    rules: list[str] | None = None,
    minutes: int = 0,
    tokens: int = 1000,
    status: ProjectVideoProcedureStatus = ProjectVideoProcedureStatus.APPROVED,
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
                ProcedureStep(
                    step=index + 1,
                    action=action,
                    source_timestamps=[f"01:0{index}"],
                )
                for index, action in enumerate(actions)
            ],
            rules=rules or [],
        ),
        cloud_calls_made=1,
        usage=GeminiUsage(total_tokens=tokens),
        created_at=BASE + timedelta(minutes=minutes),
    )


def test_an_unchanged_step_is_reported_as_unchanged() -> None:
    diff = diff_versions(
        record("vpr_a", 1, ["Push off with the hips."]),
        record("vpr_b", 2, ["Push off with the hips"], minutes=5),
    )

    assert diff.steps[0].kind is StepChangeKind.UNCHANGED
    assert diff.unchanged_step_count == 1
    assert diff.has_changes is False


def test_a_rewritten_step_shows_both_sides() -> None:
    diff = diff_versions(
        record("vpr_a", 1, ["Push off with the hips."]),
        record("vpr_b", 2, ["Drive the knee forward."], minutes=5),
    )

    step = diff.steps[0]
    assert step.kind is StepChangeKind.CHANGED
    assert step.before == "Push off with the hips."
    assert step.after == "Drive the knee forward."
    assert diff.changed_step_count == 1
    assert diff.has_changes is True


def test_added_and_removed_steps_are_counted_separately() -> None:
    grew = diff_versions(
        record("vpr_a", 1, ["One."]),
        record("vpr_b", 2, ["One.", "Two."], minutes=5),
    )
    shrank = diff_versions(
        record("vpr_a", 1, ["One.", "Two."]),
        record("vpr_b", 2, ["One."], minutes=5),
    )

    assert grew.added_step_count == 1
    assert grew.steps[1].kind is StepChangeKind.ADDED
    assert grew.steps[1].before is None
    assert shrank.removed_step_count == 1
    assert shrank.steps[1].kind is StepChangeKind.REMOVED
    assert shrank.steps[1].after is None


def test_rules_gained_and_lost_are_reported() -> None:
    diff = diff_versions(
        record("vpr_a", 1, ["One."], rules=["Keep the torso upright."]),
        record("vpr_b", 2, ["One."], rules=["Land mid-foot."], minutes=5),
    )

    rules = next(item for item in diff.lists if item.field == "rules")
    assert rules.added == ["Land mid-foot."]
    assert rules.removed == ["Keep the torso upright."]
    assert diff.has_changes is True


def test_a_diff_across_two_sources_says_so() -> None:
    same = diff_versions(
        record("vpr_a", 1, ["One."]),
        record("vpr_b", 2, ["One."], minutes=5),
    )
    across = diff_versions(
        record("vpr_a", 1, ["One."]),
        record("vpr_b", 2, ["One."], source_url="https://youtu.be/other", minutes=5),
    )

    assert same.same_source is True
    assert across.same_source is False
    assert across.to_source_url == "https://youtu.be/other"


def test_a_diff_never_claims_authority_over_the_versions() -> None:
    diff = diff_versions(
        record("vpr_a", 1, ["One."]),
        record("vpr_b", 2, ["Two."], minutes=5),
    )

    assert diff.is_advisory is True


def test_history_totals_the_calls_and_tokens_it_actually_holds() -> None:
    history = build_history(
        "prj_history01",
        [
            record("vpr_a", 1, ["One."], tokens=1200),
            record("vpr_b", 2, ["Two."], minutes=5, tokens=800),
        ],
    )

    assert [item.extraction_id for item in history.versions] == ["vpr_a", "vpr_b"]
    assert history.total_cloud_calls == 2
    assert history.total_tokens == 2000
    assert history.latest_diff is not None
    assert history.latest_diff.from_extraction_id == "vpr_a"
    assert history.latest_diff.to_extraction_id == "vpr_b"


def test_a_single_version_has_nothing_to_diff_against() -> None:
    history = build_history("prj_history01", [record("vpr_a", 1, ["One."])])

    assert len(history.versions) == 1
    assert history.latest_diff is None


def test_a_failed_extraction_is_listed_but_never_diffed() -> None:
    failed = ProjectVideoProcedureRecord(
        extraction_id="vpr_failed",
        project_id="prj_history01",
        source_url="https://youtu.be/-fD2TSL2s7I",
        status=ProjectVideoProcedureStatus.EXTRACTION_FAILED,
        cloud_calls_made=1,
        failure_code="quota_exceeded",
        created_at=BASE + timedelta(minutes=9),
    )

    history = build_history(
        "prj_history01",
        [record("vpr_a", 1, ["One."]), failed],
    )

    assert len(history.versions) == 2
    assert history.versions[1].step_count == 0
    assert history.latest_diff is None


def test_the_endpoints_return_history_and_an_explicit_diff() -> None:
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
    for extraction_id, version, actions, minutes in (
        ("vpr_hist_one", 1, ["Push off with the hips."], 0),
        ("vpr_hist_two", 2, ["Drive the knee forward."], 5),
    ):
        stored = record(
            extraction_id,
            version,
            actions,
            project_id=project_id,
            minutes=minutes,
        )
        project_video_procedure_service._records[extraction_id] = stored

    history = client.get(f"/api/projects/{project_id}/video-procedures/history/versions")
    diff = client.get(
        f"/api/projects/{project_id}/video-procedures/history/diff"
        "/vpr_hist_one/vpr_hist_two"
    )

    assert history.status_code == 200
    assert len(history.json()["versions"]) == 2
    assert history.json()["latest_diff"]["changed_step_count"] == 1
    assert diff.status_code == 200
    assert diff.json()["from_version"] == 1
    assert diff.json()["to_version"] == 2
    assert diff.json()["is_advisory"] is True


def test_history_for_an_unknown_project_is_not_found() -> None:
    response = client.get("/api/projects/prj_missing/video-procedures/history/versions")

    assert response.status_code == 404
