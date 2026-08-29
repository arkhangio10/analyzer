"""Safe computer-procedure validation contracts."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ComputerActionKind(StrEnum):
    """Actions representable without permitting arbitrary shell commands."""

    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE_TEXT = "type_text"
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"


class ComputerAction(BaseModel):
    """One inspectable action in a computer procedure."""

    action_id: str = Field(min_length=1, max_length=80)
    kind: ComputerActionKind
    target: str = Field(min_length=1, max_length=500)
    value_template: str | None = Field(default=None, max_length=2000)


class ComputerPlanValidationRequest(BaseModel):
    """A proposed plan that must remain validation-only in this phase."""

    project_id: str = Field(min_length=1, max_length=120)
    application: str = Field(min_length=1, max_length=160)
    actions: list[ComputerAction] = Field(min_length=1, max_length=100)
    sandbox_required: Literal[True] = True
    dry_run: Literal[True] = True


class ComputerPlanValidationResult(BaseModel):
    """Auditable validation result with proof that no host action ran."""

    project_id: str
    accepted: bool
    normalized_actions: list[ComputerAction]
    violations: list[str] = Field(default_factory=list)
    execution_mode: Literal["validation_only"] = "validation_only"
    host_actions_made: Literal[0] = 0
    cloud_calls_made: Literal[0] = 0


class ComputerActionStatus(StrEnum):
    """Observable outcome for one attempted sandbox action."""

    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class ComputerExecutionStatus(StrEnum):
    """Aggregate state for one bounded sandbox execution."""

    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    BLOCKED = "blocked"
    REJECTED = "rejected"


class ComputerSandboxExecutionRequest(BaseModel):
    """Explicitly approved execution in the managed local filesystem sandbox."""

    project_id: str = Field(min_length=1, max_length=120)
    application: str = Field(min_length=1, max_length=160)
    actions: list[ComputerAction] = Field(min_length=1, max_length=100)
    input_files: dict[str, str] = Field(default_factory=dict)
    sandbox_required: Literal[True] = True
    acknowledge_local_sandbox_write: Literal[True]

    @field_validator("input_files")
    @classmethod
    def limit_input_files(cls, value: dict[str, str]) -> dict[str, str]:
        if len(value) > 20:
            raise ValueError("At most 20 input files may seed one sandbox.")
        if sum(len(content.encode("utf-8")) for content in value.values()) > 262_144:
            raise ValueError("Sandbox input files may total at most 256 KiB.")
        return value


class ComputerActionExecution(BaseModel):
    """Redacted evidence for one sandbox action."""

    action_id: str
    kind: ComputerActionKind
    status: ComputerActionStatus
    target: str
    bytes_processed: int = Field(default=0, ge=0)
    content_sha256: str | None = None
    message: str


class ComputerSandboxExecutionResult(BaseModel):
    """Auditable sandbox result that does not expose file contents."""

    execution_id: str
    project_id: str
    status: ComputerExecutionStatus
    sandbox_uri: str
    actions: list[ComputerActionExecution]
    violations: list[str] = Field(default_factory=list)
    external_host_actions_made: Literal[0] = 0
    cloud_calls_made: Literal[0] = 0
    browser_adapter_available: Literal[False] = False
