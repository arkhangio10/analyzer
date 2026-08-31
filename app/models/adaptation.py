"""Contracts for adapting a reviewed procedure to an execution destination.

Adaptation is the step between "a person approved this description" and
"something could run it". It never executes anything and never invents the
evidence a destination needs. A step the source does not describe precisely
enough is reported as blocked, with the specific evidence that is missing, so
the gap stays visible instead of being filled with a plausible guess.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.models.project import ExecutionDestination


class AdaptationReadiness(StrEnum):
    """How far one reviewed step is from something a destination could run."""

    ACTIONABLE = "actionable"
    NEEDS_HUMAN_DETAIL = "needs_human_detail"
    NOT_REPRESENTABLE = "not_representable"


class AdaptationActionKind(StrEnum):
    """Action shapes an approved adapter already supports."""

    NAVIGATE = "navigate"
    TYPE_TEXT = "type_text"
    CLICK = "click"
    MOTION_SEGMENT = "motion_segment"


class AdaptedStep(BaseModel):
    """One reviewed step and how close it is to being executable."""

    order: int = Field(ge=1)
    source_step_order: int = Field(ge=1)
    source_action: str = Field(min_length=1, max_length=2000)
    source_timestamps: list[str] = Field(default_factory=list, max_length=20)
    readiness: AdaptationReadiness
    proposed_action_kind: AdaptationActionKind | None = None
    proposed_target: str | None = Field(default=None, max_length=500)
    missing_evidence: list[str] = Field(default_factory=list, max_length=12)


class DestinationAdaptationPlan(BaseModel):
    """A proposal for one destination, never an authorization to execute.

    `approved_for_execution` is permanently false in this contract. Running any
    part of a plan requires the destination's own approval gate, which takes an
    explicit human acknowledgement of the exact actions and, for a browser, the
    exact host.
    """

    plan_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    extraction_id: str = Field(min_length=1)
    procedure_version: int = Field(ge=1)
    destination: ExecutionDestination
    steps: list[AdaptedStep] = Field(default_factory=list, max_length=500)
    actionable_step_count: int = Field(ge=0)
    blocked_step_count: int = Field(ge=0)
    missing_evidence: list[str] = Field(default_factory=list, max_length=40)
    requires_human_completion: bool
    execution_blocked_reason: str | None = Field(default=None, max_length=500)
    motion_analysis_id: str | None = Field(default=None, max_length=120)
    motion_evidence_step_count: int = Field(default=0, ge=0)
    approved_for_execution: Literal[False] = False
    simulation_only: Literal[True] = True
    cloud_calls_made: Literal[0] = 0
