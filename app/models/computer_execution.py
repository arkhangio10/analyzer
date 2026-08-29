"""Safe computer-procedure validation contracts."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


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
