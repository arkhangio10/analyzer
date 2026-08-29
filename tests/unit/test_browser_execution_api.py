"""Tests for the guarded computer-browser boundary."""

import asyncio
import socket

from fastapi.testclient import TestClient

from app.main import app
from app.models.browser_execution import ComputerBrowserExecutionRequest
from app.services.browser_execution_service import (
    BrowserExecutionService,
    PublicHostPolicy,
)


client = TestClient(app)


def browser_request(**overrides: object) -> ComputerBrowserExecutionRequest:
    payload: dict[str, object] = {
        "project_id": "prj_browser",
        "application": "Chromium",
        "actions": [
            {
                "action_id": "open",
                "kind": "navigate",
                "target": "https://example.com/form?private=value",
            },
            {
                "action_id": "type-name",
                "kind": "type_text",
                "target": "input[name='display-name']",
                "value_template": "Ada",
            },
        ],
        "approved_hosts": ["example.com"],
        "sandbox_required": True,
        "network_policy": "approved_hosts_only",
        "acknowledge_external_network": True,
        "action_timeout_ms": 2_000,
    }
    payload.update(overrides)
    return ComputerBrowserExecutionRequest.model_validate(payload)


def test_browser_endpoint_requires_explicit_network_acknowledgement() -> None:
    response = client.post(
        "/api/execution/computer/browser/execute",
        json={
            "project_id": "prj_browser",
            "application": "Chromium",
            "actions": [
                {
                    "action_id": "open",
                    "kind": "navigate",
                    "target": "https://example.com",
                }
            ],
            "approved_hosts": ["example.com"],
            "sandbox_required": True,
        },
    )

    assert response.status_code == 422


def test_disabled_browser_is_rejected_and_evidence_is_retrievable() -> None:
    response = client.post(
        "/api/execution/computer/browser/execute",
        json=browser_request().model_dump(mode="json"),
    )

    assert response.status_code == 201
    execution = response.json()
    assert execution["status"] == "rejected"
    assert execution["browser_adapter_available"] is False
    assert execution["external_network_requests"] == 0
    assert execution["cloud_calls_made"] == 0
    assert any("application_container" in item for item in execution["violations"])

    get_response = client.get(
        f"/api/execution/computer/browser/executions/{execution['execution_id']}"
    )
    assert get_response.status_code == 200
    assert get_response.json() == execution


def test_policy_rejects_unapproved_hosts_private_ips_and_sensitive_inputs() -> None:
    service = BrowserExecutionService(
        enabled=True,
        isolation_boundary="application_container",
    )
    request = browser_request(
        approved_hosts=["127.0.0.1"],
        actions=[
            {
                "action_id": "open-other",
                "kind": "navigate",
                "target": "https://example.com",
            },
            {
                "action_id": "password",
                "kind": "type_text",
                "target": "input[name='password']",
                "value_template": "${ENV:PASSWORD}",
            },
        ],
    )

    result = asyncio.run(service.execute(request))

    assert result.status == "rejected"
    assert result.actions == []
    assert any("private" in item for item in result.violations)
    assert any("not explicitly approved" in item for item in result.violations)
    assert any("never resolved" in item for item in result.violations)
    assert any("sensitive form fields" in item for item in result.violations)


def test_public_host_policy_blocks_private_dns_answers(monkeypatch) -> None:
    def private_dns(*_args: object, **_kwargs: object) -> list[tuple]:
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.10.0.5", 0))]

    monkeypatch.setattr(socket, "getaddrinfo", private_dns)
    policy = PublicHostPolicy(["internal.example"])

    assert asyncio.run(policy.permits_url("https://internal.example/task")) is False


def test_navigation_evidence_removes_query_and_fragment() -> None:
    redacted = BrowserExecutionService._redact_url(
        "https://example.com/form?token=secret#section"
    )

    assert redacted == "https://example.com/form"


def test_policy_rejects_nonstandard_web_ports() -> None:
    policy = PublicHostPolicy(["example.com"])

    assert "port 8443" in (
        policy.validate_url_syntax("https://example.com:8443/task") or ""
    )


def test_browser_result_contract_does_not_expose_typed_values_or_page_content() -> None:
    schema = client.get("/openapi.json").json()
    properties = schema["components"]["schemas"][
        "ComputerBrowserActionExecution"
    ]["properties"]

    assert "value_template" not in properties
    assert "page_content" not in properties
    assert "page_title" not in properties
    assert "page_title_sha256" in properties
