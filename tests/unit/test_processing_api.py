"""API tests for visible robot-motion processing sessions."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_and_get_processing_session() -> None:
    response = client.post(
        "/api/processing/robot-motion",
        json={
            "task_name": "Move a fragile component",
            "objective": "Learn a safe simulated pick-and-place procedure.",
            "source": "ui-reference://robot-demo",
            "language": "es",
            "simulation_only": True,
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["status"] == "processing"
    assert created["execution_mode"] == "local_simulation"
    assert created["cloud_calls_made"] == 0
    assert created["requested_cloud_model"] == "gemini-3.5-flash-lite"

    get_response = client.get(
        f"/api/processing/robot-motion/{created['session_id']}"
    )
    assert get_response.status_code == 200
    assert get_response.json()["session_id"] == created["session_id"]


def test_processing_session_requires_simulation_only() -> None:
    response = client.post(
        "/api/processing/robot-motion",
        json={
            "task_name": "Move a component",
            "objective": "Test hardware mode.",
            "source": "ui-reference://robot-demo",
            "language": "en",
            "simulation_only": False,
        },
    )

    assert response.status_code == 422


def test_unknown_processing_session_returns_not_found() -> None:
    response = client.get("/api/processing/robot-motion/missing")

    assert response.status_code == 404

