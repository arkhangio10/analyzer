"""API tests for destination-aware project intake."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_computer_project_uses_safe_defaults_and_asks_one_question() -> None:
    response = client.post(
        "/api/projects",
        json={
            "task_description": "Organiza las facturas recibidas en carpetas por proveedor.",
            "destination": "computer",
            "language": "es",
        },
    )

    assert response.status_code == 201
    project = response.json()
    assert project["destination_contract"]["destination"] == "computer"
    assert project["destination_contract"]["operating_system"] == "auto-detect"
    assert project["destination_contract"]["sandbox_required"] is True
    assert project["is_sufficiently_clear"] is False
    assert project["next_action"] == "collect_details"
    assert len(project["clarification_questions"]) == 1
    assert project["clarification_questions"][0]["field"] == "computer_application"


def test_robot_project_is_ready_when_model_is_supplied() -> None:
    response = client.post(
        "/api/projects",
        json={
            "task_description": "Aprende a correr con una marcha inspirada en un perro.",
            "destination": "robot",
            "language": "es",
            "robot_model": "Unitree Go2",
            "robot_class": "quadruped",
        },
    )

    assert response.status_code == 201
    project = response.json()
    contract = project["destination_contract"]
    assert contract["destination"] == "robot"
    assert contract["profile_standard"] == "ARP-1"
    assert contract["simulation_only"] is True
    assert contract["hardware_execution_approved"] is False
    assert project["clarification_questions"] == []
    assert project["is_sufficiently_clear"] is True
    assert project["next_action"] == "choose_source"

    get_response = client.get(f"/api/projects/{project['project_id']}")
    assert get_response.status_code == 200
    assert get_response.json()["project_id"] == project["project_id"]


def test_robot_project_asks_only_for_the_exact_model() -> None:
    response = client.post(
        "/api/projects",
        json={
            "task_description": "Aprende a tomar una pieza y colocarla con precisión.",
            "destination": "robot",
            "language": "en",
        },
    )

    assert response.status_code == 201
    project = response.json()
    assert len(project["clarification_questions"]) == 1
    assert project["clarification_questions"][0]["field"] == "robot_model"
    assert project["destination_contract"]["simulator"] == "auto-select"


def test_unknown_project_returns_not_found() -> None:
    response = client.get("/api/projects/prj_missing")
    assert response.status_code == 404


def test_projects_can_be_listed_for_reopening() -> None:
    created = client.post(
        "/api/projects",
        json={
            "task_description": "Teach a robot arm to place a fragile component.",
            "destination": "robot",
            "robot_model": "APRENDIZ SimArm-6",
            "language": "en",
        },
    ).json()

    listed = client.get("/api/projects")

    assert listed.status_code == 200
    assert created["project_id"] in [
        project["project_id"] for project in listed.json()
    ]


def test_video_procedures_can_be_listed_for_a_project() -> None:
    created = client.post(
        "/api/projects",
        json={
            "task_description": "Teach a robot arm to place a fragile component.",
            "destination": "robot",
            "robot_model": "APRENDIZ SimArm-6",
            "language": "en",
        },
    ).json()

    listed = client.get(
        f"/api/projects/{created['project_id']}/video-procedures"
    )

    assert listed.status_code == 200
    assert listed.json() == []


def test_listing_video_procedures_for_an_unknown_project_is_visible() -> None:
    response = client.get("/api/projects/prj_missing00000/video-procedures")

    assert response.status_code == 404
