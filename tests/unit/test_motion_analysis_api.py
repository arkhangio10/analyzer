"""Tests for the motion-analysis endpoints and their refusals."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.runtime import motion_analysis_service, project_video_procedure_service
from app.main import app
from app.models.motion_analysis import (
    MotionAnalysisCall,
    ObservedMotionPhase,
    ObservedMotionReport,
    ProviderJointSample,
)
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)
from app.services.gemini_service import GeminiConfigurationError, GeminiProviderError


client = TestClient(app)


class StubGemini:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.call_count = 0

    async def analyze_motion(self, **kwargs: object) -> MotionAnalysisCall:
        self.call_count += 1
        if self.error:
            raise self.error
        return MotionAnalysisCall(
            report=ObservedMotionReport(
                subject_kind="human_body",
                kinematic_chain="bipedal_lower_limb",
                phases=[
                    ObservedMotionPhase(
                        name="stance",
                        start_seconds=0.0,
                        end_seconds=1.0,
                        description="Weight rests on one leg.",
                    )
                ],
                samples=[
                    ProviderJointSample(
                        t=round(60 + index * 0.25, 3),
                        j=f"{side}.hip",
                        a=10.0 + index,
                        c=0.7,
                        v="partial",
                    )
                    for index in range(12)
                    for side in ("left", "right")
                ],
                uncertainties=["Clothing hides the knees."],
            ),
            provider="vertex_ai",
            requested_model="gemini-test",
            model_version="gemini-test-001",
            elapsed_seconds=2.0,
        )


def create_robot_project() -> dict:
    response = client.post(
        "/api/projects",
        json={
            "task_description": "Learn the walking mechanics demonstrated in the video.",
            "destination": "robot",
            "language": "en",
            "robot_model": "APRENDIZ SimArm-6",
            "robot_class": "arm",
        },
    )
    assert response.status_code == 201
    return response.json()


def store_record(
    project_id: str,
    status: ProjectVideoProcedureStatus,
) -> ProjectVideoProcedureRecord:
    record = ProjectVideoProcedureRecord(
        extraction_id=f"vpr_motion_{status.value}_{uuid4().hex[:8]}",
        project_id=project_id,
        procedure_version=1,
        source_url="https://youtu.be/-fD2TSL2s7I",
        status=status,
        created_at=datetime.now(timezone.utc),
    )
    project_video_procedure_service._records[record.extraction_id] = record
    return record


def use(stub: StubGemini) -> None:
    motion_analysis_service._gemini_service = stub


def payload(**overrides: object) -> dict:
    body: dict[str, object] = {"acknowledge_cloud_cost": True, "output_language": "en"}
    body.update(overrides)
    return body


def test_analysis_requires_an_acknowledged_cost() -> None:
    project = create_robot_project()
    record = store_record(project["project_id"], ProjectVideoProcedureStatus.APPROVED)
    stub = StubGemini()
    use(stub)

    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{record.extraction_id}/motion-analysis",
        json={"output_language": "en"},
    )

    assert response.status_code == 422
    assert stub.call_count == 0


def test_an_unapproved_procedure_is_refused_with_409() -> None:
    project = create_robot_project()
    record = store_record(
        project["project_id"],
        ProjectVideoProcedureStatus.AWAITING_REVIEW,
    )
    stub = StubGemini()
    use(stub)

    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{record.extraction_id}/motion-analysis",
        json=payload(),
    )

    assert response.status_code == 409
    assert "already approved" in response.json()["detail"]
    assert stub.call_count == 0


def test_a_window_beyond_the_budget_is_refused_before_the_call() -> None:
    project = create_robot_project()
    record = store_record(project["project_id"], ProjectVideoProcedureStatus.APPROVED)
    stub = StubGemini()
    use(stub)

    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{record.extraction_id}/motion-analysis",
        json=payload(frames_per_second=8.0, window_seconds=90.0),
    )

    assert response.status_code == 422
    assert "nothing was billed" in response.json()["detail"]
    assert stub.call_count == 0


def test_an_approved_procedure_is_analysed_and_audited() -> None:
    project = create_robot_project()
    record = store_record(project["project_id"], ProjectVideoProcedureStatus.APPROVED)
    use(StubGemini())

    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{record.extraction_id}/motion-analysis",
        json=payload(frames_per_second=4.0, window_start_seconds=60.0, window_seconds=12.0),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["sample_count"] == 24
    assert body["requested_fps"] == 4.0
    assert body["physically_measured"] is False
    assert body["measurement_method"] == "vision_model_estimate"
    assert body["audit"]["verdict"] == "not_evidence"
    assert body["retarget"]["retarget_supported"] is False
    assert body["retarget"]["approved_for_execution"] is False
    assert body["cloud_calls_made"] == 1


def test_the_retained_analysis_can_be_read_back_without_paying_again() -> None:
    project = create_robot_project()
    record = store_record(project["project_id"], ProjectVideoProcedureStatus.APPROVED)
    stub = StubGemini()
    use(stub)
    url = (
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{record.extraction_id}/motion-analysis"
    )

    assert client.get(url).status_code == 404
    created = client.post(url, json=payload())
    assert created.status_code == 201

    fetched = client.get(url)

    assert fetched.status_code == 200
    assert fetched.json()["analysis_id"] == created.json()["analysis_id"]
    assert stub.call_count == 1


def test_a_disabled_provider_reports_503_and_a_failure_reports_502() -> None:
    project = create_robot_project()
    record = store_record(project["project_id"], ProjectVideoProcedureStatus.APPROVED)
    url = (
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{record.extraction_id}/motion-analysis"
    )

    use(StubGemini(GeminiConfigurationError("Gemini calls are disabled.")))
    disabled = client.post(url, json=payload())

    use(StubGemini(GeminiProviderError("quota_exceeded", http_status=429)))
    failed = client.post(url, json=payload())

    assert disabled.status_code == 503
    assert failed.status_code == 502
    assert "quota_exceeded" in failed.json()["detail"]
    assert "may have been billed" in failed.json()["detail"]


def test_an_unknown_extraction_is_not_found() -> None:
    project = create_robot_project()
    use(StubGemini())

    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/"
        "vpr_missing/motion-analysis",
        json=payload(),
    )

    assert response.status_code == 404
