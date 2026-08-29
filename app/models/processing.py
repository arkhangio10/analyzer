"""Typed contracts for visible backend processing sessions."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.models.evaluation import EvaluationResult
from app.models.robot_motion import RobotMotionTrainingResult


class ProcessingStatus(StrEnum):
    """Lifecycle states exposed to the product interface."""

    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RobotMotionProcessingRequest(BaseModel):
    """Start one safe, local robot-motion processing demonstration."""

    task_name: str = Field(min_length=1, max_length=160)
    objective: str = Field(min_length=1, max_length=500)
    source: str = Field(min_length=1, max_length=500)
    language: Literal["es", "en"] = "es"
    simulation_only: Literal[True] = True


class RobotMotionProcessingSession(BaseModel):
    """Inspectable state for one backend-driven processing session."""

    session_id: str = Field(min_length=1)
    status: ProcessingStatus
    progress_percent: int = Field(ge=0, le=100)
    current_stage_index: int | None = Field(default=None, ge=0, le=4)
    completed_stage_count: int = Field(ge=0, le=5)
    stage_count: Literal[5] = 5
    execution_mode: Literal["local_simulation"] = "local_simulation"
    cloud_calls_made: Literal[0] = 0
    requested_cloud_model: str = "gemini-3.5-flash-lite"
    training_result: RobotMotionTrainingResult | None = None
    evaluation_result: EvaluationResult | None = None

