"""Typed contracts for safe robot-motion procedural learning."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.models.procedure import Procedure


class RobotMotionTrainingStatus(StrEnum):
    """Outcome of deterministic demonstration processing."""

    PROCEDURE_EXTRACTED = "procedure_extracted"
    REJECTED = "rejected"


class JointLimit(BaseModel):
    """Instructor-supplied safe operating envelope for one robot joint."""

    joint_index: int = Field(ge=0)
    minimum_degrees: float
    maximum_degrees: float
    maximum_velocity_degrees_per_second: float = Field(gt=0)


class MotionWaypoint(BaseModel):
    """One observed robot pose at a specific point in a demonstration."""

    timestamp_seconds: float = Field(ge=0)
    joint_positions_degrees: list[float] = Field(min_length=1, max_length=32)
    gripper_percent: float | None = Field(default=None, ge=0, le=100)
    label: str | None = Field(default=None, max_length=120)


class RobotMotionTrainingRequest(BaseModel):
    """A structured instructor demonstration used to acquire a procedure."""

    task_name: str = Field(min_length=1, max_length=160)
    objective: str = Field(min_length=1, max_length=500)
    robot_model: str = Field(min_length=1, max_length=120)
    demonstration_id: str = Field(min_length=1, max_length=120)
    source: str = Field(min_length=1, max_length=500)
    waypoints: list[MotionWaypoint] = Field(min_length=2, max_length=500)
    joint_limits: list[JointLimit] = Field(min_length=1, max_length=32)
    instructor_verified: bool = False
    simulation_only: Literal[True] = True


class RobotMotionMetrics(BaseModel):
    """Deterministic measurements retained with learned procedural memory."""

    duration_seconds: float = Field(ge=0)
    path_length_degrees: float = Field(ge=0)
    peak_velocity_degrees_per_second: float = Field(ge=0)
    waypoint_count: int = Field(ge=0)
    joint_count: int = Field(ge=0)


class RobotMotionTrainingResult(BaseModel):
    """Transparent outcome of processing one motion demonstration."""

    session_id: str = Field(min_length=1)
    status: RobotMotionTrainingStatus
    safety_passed: bool
    safety_violations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metrics: RobotMotionMetrics | None = None
    procedure: Procedure | None = None
    learning_level: Literal["observation"] = "observation"
    validation_scope: Literal["not_validated", "instructor_demonstration"]


class RobotMotionEvaluationRequest(BaseModel):
    """Candidate execution compared with a stored instructor demonstration."""

    execution_id: str = Field(min_length=1, max_length=120)
    waypoints: list[MotionWaypoint] = Field(min_length=2, max_length=500)
    joint_tolerance_degrees: float = Field(default=5, gt=0, le=45)
    duration_tolerance_seconds: float = Field(default=0.5, ge=0, le=30)
