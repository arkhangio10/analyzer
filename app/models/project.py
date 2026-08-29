"""Project intake and execution-destination contracts."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.models.task import TaskDefinition


class ExecutionDestination(StrEnum):
    """Supported destinations for a learned procedure."""

    COMPUTER = "computer"
    ROBOT = "robot"


class ComputerExecutionContract(BaseModel):
    """Safe initial contract for a procedure executed on a computer."""

    destination: Literal[ExecutionDestination.COMPUTER] = ExecutionDestination.COMPUTER
    operating_system: str = "auto-detect"
    application: str | None = None
    locale: Literal["es", "en"] = "es"
    allowed_actions: list[str] = Field(
        default_factory=lambda: ["browser", "keyboard", "mouse", "files"]
    )
    sandbox_required: bool = True


class RobotExecutionContract(BaseModel):
    """Simulation-first contract for a physical robot destination."""

    destination: Literal[ExecutionDestination.ROBOT] = ExecutionDestination.ROBOT
    robot_model: str | None = None
    robot_class: str = "unknown"
    profile_standard: Literal["ARP-1"] = "ARP-1"
    simulator: str = "auto-select"
    simulation_only: bool = True
    hardware_execution_approved: bool = False


DestinationContract = Annotated[
    ComputerExecutionContract | RobotExecutionContract,
    Field(discriminator="destination"),
]


class ProjectClarificationRequest(BaseModel):
    """Minimum information supplied by the user at project creation."""

    task_description: str = Field(min_length=12, max_length=4000)
    destination: ExecutionDestination
    language: Literal["es", "en"] = "es"
    computer_application: str | None = Field(default=None, max_length=160)
    computer_os: str | None = Field(default=None, max_length=80)
    robot_model: str | None = Field(default=None, max_length=160)
    robot_class: str | None = Field(default=None, max_length=80)


class ClarificationQuestion(BaseModel):
    """One blocking question needed to complete the destination contract."""

    id: str
    field: str
    question: str
    reason: str


class ProjectDraft(BaseModel):
    """Clarified project ready to continue into source selection."""

    project_id: str
    task_definition: TaskDefinition
    destination_contract: DestinationContract
    clarification_questions: list[ClarificationQuestion] = Field(
        default_factory=list,
        max_length=1,
    )
    defaults_applied: list[str] = Field(default_factory=list)
    is_sufficiently_clear: bool
    next_action: Literal["collect_details", "choose_source"]
