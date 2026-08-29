"""API tests for the robot-motion training vertical slice."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def valid_payload() -> dict[str, object]:
    return {
        "task_name": "Move a component between trays",
        "objective": "Learn a safe pick-and-place joint trajectory.",
        "robot_model": "SimArm-2",
        "demonstration_id": "demo-api-001",
        "source": "instructor://robotics-lab/api-demo",
        "waypoints": [
            {
                "timestamp_seconds": 0,
                "joint_positions_degrees": [0, 0],
                "gripper_percent": 100,
                "label": "home",
            },
            {
                "timestamp_seconds": 1,
                "joint_positions_degrees": [10, 5],
                "gripper_percent": 40,
                "label": "pick",
            },
            {
                "timestamp_seconds": 2,
                "joint_positions_degrees": [20, 10],
                "gripper_percent": 40,
                "label": "place",
            },
        ],
        "joint_limits": [
            {
                "joint_index": 0,
                "minimum_degrees": -90,
                "maximum_degrees": 90,
                "maximum_velocity_degrees_per_second": 20,
            },
            {
                "joint_index": 1,
                "minimum_degrees": -45,
                "maximum_degrees": 45,
                "maximum_velocity_degrees_per_second": 10,
            },
        ],
        "instructor_verified": True,
        "simulation_only": True,
    }


def test_robot_motion_training_api_round_trip() -> None:
    create_response = client.post(
        "/api/training/robot-motion",
        json=valid_payload(),
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "procedure_extracted"
    assert created["safety_passed"] is True
    assert created["procedure"]["steps"]

    get_response = client.get(
        f"/api/training/robot-motion/{created['session_id']}"
    )
    assert get_response.status_code == 200
    assert get_response.json() == created

    evaluation_response = client.post(
        f"/api/training/robot-motion/{created['session_id']}/evaluate",
        json={
            "execution_id": "api-execution-001",
            "waypoints": valid_payload()["waypoints"],
        },
    )
    assert evaluation_response.status_code == 200
    assert evaluation_response.json()["passed"] is True


def test_hardware_execution_cannot_be_enabled_through_training_api() -> None:
    payload = valid_payload()
    payload["simulation_only"] = False

    response = client.post("/api/training/robot-motion", json=payload)

    assert response.status_code == 422


def test_unknown_robot_motion_session_returns_not_found() -> None:
    response = client.get("/api/training/robot-motion/does-not-exist")

    assert response.status_code == 404


def test_rejected_demonstration_cannot_be_evaluated() -> None:
    payload = valid_payload()
    payload["waypoints"][1]["joint_positions_degrees"] = [100, 5]
    create_response = client.post(
        "/api/training/robot-motion",
        json=payload,
    )
    created = create_response.json()

    assert create_response.status_code == 201
    assert created["status"] == "rejected"

    evaluation_response = client.post(
        f"/api/training/robot-motion/{created['session_id']}/evaluate",
        json={
            "execution_id": "rejected-execution",
            "waypoints": valid_payload()["waypoints"],
        },
    )
    assert evaluation_response.status_code == 409
