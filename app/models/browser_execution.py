"""Guarded browser-execution contracts."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.computer_execution import (
    ComputerAction,
    ComputerActionKind,
    ComputerActionStatus,
    ComputerExecutionStatus,
)


class ComputerBrowserExecutionRequest(BaseModel):
    """An explicitly approved browser run with a closed network allowlist."""

    project_id: str = Field(min_length=1, max_length=120)
    application: str = Field(min_length=1, max_length=160)
    actions: list[ComputerAction] = Field(min_length=1, max_length=25)
    approved_hosts: list[str] = Field(min_length=1, max_length=12)
    sandbox_required: Literal[True] = True
    network_policy: Literal["approved_hosts_only"] = "approved_hosts_only"
    acknowledge_external_network: Literal[True]
    action_timeout_ms: int = Field(default=10_000, ge=500, le=15_000)

    @field_validator("approved_hosts")
    @classmethod
    def normalize_approved_hosts(cls, value: list[str]) -> list[str]:
        normalized = [host.strip().casefold().rstrip(".") for host in value]
        if any(not host for host in normalized):
            raise ValueError("Approved hosts cannot be empty.")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Approved hosts must be unique.")
        return normalized


class ComputerBrowserActionExecution(BaseModel):
    """Redacted evidence for one browser action."""

    action_id: str
    kind: ComputerActionKind
    status: ComputerActionStatus
    target: str
    observed_url: str | None = None
    page_title_sha256: str | None = None
    page_title_length: int = Field(default=0, ge=0)
    message: str


class ComputerBrowserExecutionResult(BaseModel):
    """Auditable browser result without typed values or page content."""

    execution_id: str
    project_id: str
    status: ComputerExecutionStatus
    actions: list[ComputerBrowserActionExecution]
    violations: list[str] = Field(default_factory=list)
    approved_hosts: list[str]
    network_policy: Literal["approved_hosts_only"] = "approved_hosts_only"
    external_network_requests: int = Field(default=0, ge=0)
    blocked_network_requests: int = Field(default=0, ge=0)
    cloud_calls_made: Literal[0] = 0
    browser_adapter_available: bool
    isolation_boundary: Literal[
        "managed_local_directory",
        "application_container",
    ]
