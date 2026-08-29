"""Tests for project-bound, user-approved computer rehearsals."""

import json

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_project(destination: str = "computer") -> dict:
    payload = {
        "task_description": "Complete a public browser form using reviewed sample data.",
        "destination": destination,
        "language": "en",
    }
    if destination == "computer":
        payload["computer_application"] = "Chromium"
    else:
        payload["robot_model"] = "Unitree Go2"
        payload["robot_class"] = "quadruped"
    response = client.post("/api/projects", json=payload)
    assert response.status_code == 201
    return response.json()


def practice_payload() -> dict:
    return {
        "procedure_name": "Reviewed browser rehearsal",
        "plan_origin": "user_reviewed",
        "approved_hosts": ["example.com"],
        "actions": [
            {
                "action_id": "open-target",
                "kind": "navigate",
                "target": "https://example.com/form?private=value",
            },
            {
                "action_id": "enter-sample",
                "kind": "type_text",
                "target": "input[name='display-name']",
                "value_template": "Sample value",
            },
        ],
    }


def test_computer_project_creates_retrievable_approval_draft() -> None:
    project = create_project()
    response = client.post(
        f"/api/projects/{project['project_id']}/computer-practices",
        json=practice_payload(),
    )

    assert response.status_code == 201
    practice = response.json()
    assert practice["project_id"] == project["project_id"]
    assert practice["status"] == "awaiting_approval"
    assert practice["plan_origin"] == "user_reviewed"
    assert practice["cloud_calls_made"] == 0

    get_response = client.get(
        f"/api/projects/{project['project_id']}/computer-practices/"
        f"{practice['practice_id']}"
    )
    assert get_response.status_code == 200
    assert get_response.json() == practice


def test_practice_execution_requires_both_human_acknowledgements() -> None:
    project = create_project()
    draft_response = client.post(
        f"/api/projects/{project['project_id']}/computer-practices",
        json=practice_payload(),
    )
    practice = draft_response.json()

    response = client.post(
        f"/api/projects/{project['project_id']}/computer-practices/"
        f"{practice['practice_id']}/execute",
        json={"acknowledge_external_network": True},
    )

    assert response.status_code == 422


def test_approved_practice_returns_redacted_execution_evidence() -> None:
    project = create_project()
    draft_response = client.post(
        f"/api/projects/{project['project_id']}/computer-practices",
        json=practice_payload(),
    )
    practice = draft_response.json()

    execution_url = (
        f"/api/projects/{project['project_id']}/computer-practices/"
        f"{practice['practice_id']}/execute"
    )
    approval = {
        "acknowledge_actions_reviewed": True,
        "acknowledge_external_network": True,
        "action_timeout_ms": 2_000,
    }
    response = client.post(execution_url, json=approval)

    assert response.status_code == 201
    result = response.json()
    assert result["practice"]["status"] == "rejected"
    assert result["execution"]["browser_adapter_available"] is False
    assert result["execution"]["actions"] == []
    assert result["execution"]["cloud_calls_made"] == 0
    execution_evidence = json.dumps(result["execution"])
    assert "Sample value" not in execution_evidence
    assert "private=value" not in execution_evidence

    retry_response = client.post(execution_url, json=approval)
    assert retry_response.status_code == 409


def test_robot_project_cannot_create_computer_practice() -> None:
    project = create_project("robot")

    response = client.post(
        f"/api/projects/{project['project_id']}/computer-practices",
        json=practice_payload(),
    )

    assert response.status_code == 409


def test_practice_rejects_navigation_outside_approved_hosts() -> None:
    project = create_project()
    payload = practice_payload()
    payload["approved_hosts"] = ["example.org"]

    response = client.post(
        f"/api/projects/{project['project_id']}/computer-practices",
        json=payload,
    )

    assert response.status_code == 422
    assert "not explicitly approved" in response.text
