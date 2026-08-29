"""Tests for validation-only computer plans."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.models.computer_execution import ComputerSandboxExecutionRequest
from app.services.computer_execution_service import ComputerExecutionService


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


def test_file_actions_execute_only_inside_managed_sandbox(tmp_path: Path) -> None:
    service = ComputerExecutionService(sandbox_root=tmp_path / "sandboxes")
    request = ComputerSandboxExecutionRequest.model_validate(
        {
            "project_id": "prj_files",
            "application": "File workflow",
            "input_files": {"input/source.txt": "instructor data"},
            "actions": [
                {
                    "action_id": "read-source",
                    "kind": "read_file",
                    "target": "input/source.txt",
                },
                {
                    "action_id": "write-result",
                    "kind": "write_file",
                    "target": "output/result.txt",
                    "value_template": "validated result",
                },
            ],
            "sandbox_required": True,
            "acknowledge_local_sandbox_write": True,
        }
    )

    result = service.execute(request)

    assert result.status == "completed"
    assert result.external_host_actions_made == 0
    assert result.isolation_boundary == "managed_local_directory"
    assert all(action.content_sha256 for action in result.actions)
    sandbox = tmp_path / "sandboxes" / result.execution_id
    assert (sandbox / "output" / "result.txt").read_text(encoding="utf-8") == "validated result"
    assert "instructor data" not in result.model_dump_json()


def test_execution_rejects_seed_file_outside_sandbox(tmp_path: Path) -> None:
    service = ComputerExecutionService(sandbox_root=tmp_path / "sandboxes")
    request = ComputerSandboxExecutionRequest.model_validate(
        {
            "project_id": "prj_escape",
            "application": "File workflow",
            "input_files": {"../outside.txt": "blocked"},
            "actions": [
                {
                    "action_id": "read",
                    "kind": "read_file",
                    "target": "safe.txt",
                }
            ],
            "sandbox_required": True,
            "acknowledge_local_sandbox_write": True,
        }
    )

    result = service.execute(request)

    assert result.status == "rejected"
    assert result.actions == []
    assert not (tmp_path / "outside.txt").exists()


def test_browser_actions_remain_visibly_blocked_and_retrievable() -> None:
    response = client.post(
        "/api/execution/computer/execute",
        json={
            "project_id": "prj_browser",
            "application": "Browser",
            "actions": [
                {
                    "action_id": "open",
                    "kind": "navigate",
                    "target": "https://example.com",
                }
            ],
            "sandbox_required": True,
            "acknowledge_local_sandbox_write": True,
        },
    )

    assert response.status_code == 201
    execution = response.json()
    assert execution["status"] == "blocked"
    assert execution["browser_adapter_available"] is False
    assert execution["external_host_actions_made"] == 0
    assert execution["isolation_boundary"] == "managed_local_directory"

    get_response = client.get(
        f"/api/execution/computer/executions/{execution['execution_id']}"
    )
    assert get_response.status_code == 200
    assert get_response.json() == execution
