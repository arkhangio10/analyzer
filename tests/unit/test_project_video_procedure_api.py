"""Tests for project-bound video extraction and human review."""

from fastapi.testclient import TestClient

from app.api.runtime import project_video_procedure_service
from app.main import app
from app.models.procedure import Procedure, ProcedureStep
from app.models.video_extraction import GeminiUsage, VideoExtractionResult
from app.services.gemini_service import GeminiProviderError


client = TestClient(app)


def create_project() -> dict:
    response = client.post(
        "/api/projects",
        json={
            "task_description": "Learn the observable technique demonstrated in the video.",
            "destination": "computer",
            "language": "en",
            "computer_application": "Training viewer",
        },
    )
    assert response.status_code == 201
    return response.json()


def extraction_payload() -> dict:
    return {
        "video_url": "https://www.youtube.com/watch?v=example",
        "task_hint": "Extract only observable actions.",
        "output_language": "en",
        "acknowledge_cloud_cost": True,
        "acknowledge_source_approved": True,
    }


class SuccessfulGeminiService:
    async def extract_procedure(self, request: object) -> VideoExtractionResult:
        return VideoExtractionResult(
            source_url="https://www.youtube.com/watch?v=example",
            procedure=Procedure(
                task="Walk with aligned posture",
                objective="Demonstrate the instructed walking sequence.",
                steps=[
                    ProcedureStep(
                        step=1,
                        action="Align the torso before stepping.",
                        source_timestamps=["00:10"],
                        evidence="The instructor demonstrates upright alignment.",
                    )
                ],
                uncertainties=["The camera does not show foot pressure."],
            ),
            provider="vertex_ai",
            requested_model="gemini-test",
            model_version="gemini-test-001",
            elapsed_seconds=1.25,
            usage=GeminiUsage(prompt_tokens=100, candidate_tokens=25, total_tokens=125),
        )


class FailingGeminiService:
    async def extract_procedure(self, request: object) -> VideoExtractionResult:
        raise GeminiProviderError(
            "provider_unavailable",
            http_status=500,
            provider_status="INTERNAL",
            requested_model="gemini-test",
        )


def test_project_extraction_requires_source_and_cost_approval() -> None:
    project = create_project()
    payload = extraction_payload()
    payload["acknowledge_source_approved"] = False

    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/extract",
        json=payload,
    )

    assert response.status_code == 422


def test_disabled_provider_failure_is_retained_without_a_cloud_call() -> None:
    project = create_project()

    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/extract",
        json=extraction_payload(),
    )

    assert response.status_code == 201
    record = response.json()
    assert record["status"] == "extraction_failed"
    assert record["failure_code"] == "provider_disabled"
    assert record["cloud_calls_made"] == 0
    assert record["procedure"] is None

    get_response = client.get(
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{record['extraction_id']}"
    )
    assert get_response.status_code == 200
    assert get_response.json() == record


def test_successful_extraction_waits_for_review_and_can_be_approved(monkeypatch) -> None:
    project = create_project()
    monkeypatch.setattr(
        project_video_procedure_service,
        "_gemini_service",
        SuccessfulGeminiService(),
    )

    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/extract",
        json=extraction_payload(),
    )

    assert response.status_code == 201
    record = response.json()
    assert record["status"] == "awaiting_review"
    assert record["procedure_version"] == 1
    assert record["procedure"]["steps"][0]["source_timestamps"] == ["00:10"]
    assert record["procedure"]["uncertainties"]
    assert record["usage"]["total_tokens"] == 125
    assert record["cloud_calls_made"] == 1

    review_url = (
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{record['extraction_id']}/review"
    )
    review_response = client.post(
        review_url,
        json={"decision": "approve", "notes": "Steps reviewed."},
    )
    assert review_response.status_code == 200
    assert review_response.json()["status"] == "approved"

    duplicate_review = client.post(review_url, json={"decision": "reject"})
    assert duplicate_review.status_code == 409


def test_provider_failure_retains_safe_diagnostics(monkeypatch) -> None:
    project = create_project()
    monkeypatch.setattr(
        project_video_procedure_service,
        "_gemini_service",
        FailingGeminiService(),
    )

    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/extract",
        json=extraction_payload(),
    )

    assert response.status_code == 201
    record = response.json()
    assert record["status"] == "extraction_failed"
    assert record["failure_code"] == "provider_unavailable"
    assert record["failure_http_status"] == 500
    assert record["failure_provider_status"] == "INTERNAL"
    assert record["attempted_model"] == "gemini-test"
    assert record["cloud_calls_made"] == 1


def test_failed_extraction_cannot_be_approved() -> None:
    project = create_project()
    response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/extract",
        json=extraction_payload(),
    )
    record = response.json()

    review_response = client.post(
        f"/api/projects/{project['project_id']}/video-procedures/"
        f"{record['extraction_id']}/review",
        json={"decision": "approve"},
    )

    assert review_response.status_code == 409
