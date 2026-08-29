"""User-reviewed browser-practice contracts for computer projects."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.browser_execution import ComputerBrowserExecutionResult
from app.models.computer_execution import ComputerAction


class ComputerPracticeStatus(StrEnum):
    """Lifecycle of one bounded computer rehearsal."""

    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    BLOCKED = "blocked"
    REJECTED = "rejected"


class ComputerPracticeDraftRequest(BaseModel):
    """A browser plan that the user has reviewed but not executed yet."""

    procedure_name: str = Field(min_length=3, max_length=160)
    actions: list[ComputerAction] = Field(min_length=1, max_length=25)
    approved_hosts: list[str] = Field(min_length=1, max_length=12)
    plan_origin: Literal["user_reviewed"] = "user_reviewed"

    @field_validator("approved_hosts")
    @classmethod
    def normalize_approved_hosts(cls, value: list[str]) -> list[str]:
        normalized = [host.strip().casefold().rstrip(".") for host in value]
        if any(not host for host in normalized):
            raise ValueError("Approved hosts cannot be empty.")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Approved hosts must be unique.")
        return normalized


class ComputerPracticeApprovalRequest(BaseModel):
    """Explicit approvals required immediately before external execution."""

    acknowledge_actions_reviewed: Literal[True]
    acknowledge_external_network: Literal[True]
    action_timeout_ms: int = Field(default=10_000, ge=500, le=15_000)


class ComputerPractice(BaseModel):
    """Auditable plan state attached to one computer project."""

    practice_id: str
    project_id: str
    application: str
    procedure_name: str
    plan_origin: Literal["user_reviewed"] = "user_reviewed"
    status: ComputerPracticeStatus
    actions: list[ComputerAction]
    approved_hosts: list[str]
    violations: list[str] = Field(default_factory=list)
    latest_execution_id: str | None = None
    cloud_calls_made: Literal[0] = 0


class ComputerPracticeRunResult(BaseModel):
    """Updated practice state plus redacted browser evidence."""

    practice: ComputerPractice
    execution: ComputerBrowserExecutionResult
