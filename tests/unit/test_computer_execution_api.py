"""Tests for validation-only computer plans."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_safe_computer_plan_is_accepted_without_host_actions() -> None:
    response = client.post(
        "/api/execution/computer/validate",
        json={
            "project_id": "prj_invoices",
            "application": "Google Chrome",
            "actions": [
                {
                    "action_id": "open-app",
                    "kind": "navigate",
                    "target": "https://example.com/invoices",
                },
                {
                    "action_id": "choose-filter",
                    "kind": "click",
                    "target": "button[data-action='filter']",
                },
                {
                    "action_id": "save-report",
                    "kind": "write_file",
                    "target": "reports/today.csv",
                    "value_template": "${REPORT_CONTENT}",
                },
            ],
            "sandbox_required": True,
            "dry_run": True,
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["accepted"] is True
    assert result["execution_mode"] == "validation_only"
    assert result["host_actions_made"] == 0
    assert result["cloud_calls_made"] == 0


def test_plan_rejects_host_path_embedded_credentials_and_raw_secret() -> None:
    response = client.post(
        "/api/execution/computer/validate",
        json={
            "project_id": "prj_unsafe",
            "application": "Browser",
            "actions": [
                {
                    "action_id": "bad-url",
                    "kind": "navigate",
                    "target": "https://user:password@example.com",
                },
                {
                    "action_id": "bad-file",
                    "kind": "read_file",
                    "target": "../../credentials.json",
                },
                {
                    "action_id": "raw-password",
                    "kind": "type_text",
                    "target": "input[name='password']",
                    "value_template": "plain-text-password",
                },
            ],
            "sandbox_required": True,
            "dry_run": True,
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["accepted"] is False
    assert result["host_actions_made"] == 0
    assert len(result["violations"]) == 3


def test_arbitrary_action_kind_is_rejected_by_contract() -> None:
    response = client.post(
        "/api/execution/computer/validate",
        json={
            "project_id": "prj_shell",
            "application": "PowerShell",
            "actions": [
                {"action_id": "shell", "kind": "shell", "target": "command"}
            ],
            "sandbox_required": True,
            "dry_run": True,
        },
    )
    assert response.status_code == 422
