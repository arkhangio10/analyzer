"""Project-bound extraction and human-review contracts."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.models.procedure import Procedure
from app.models.video_extraction import GeminiUsage, VideoExtractionRequest


class ProjectVideoProcedureStatus(StrEnum):
    """Lifecycle of an extracted procedure before destination adaptation."""

    EXTRACTION_FAILED = "extraction_failed"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProjectVideoProcedureExtractionRequest(VideoExtractionRequest):
    """One approved source attached to an existing project."""

    acknowledge_source_approved: Literal[True]


class ProjectVideoProcedureReviewRequest(BaseModel):
    """Human decision about one immutable extracted procedure version."""

    decision: Literal["approve", "reject"]
    notes: str | None = Field(default=None, max_length=2000)


class ProjectVideoProcedureRecord(BaseModel):
    """Persisted in-process extraction evidence and review state."""

    extraction_id: str
    project_id: str
    procedure_version: int | None = Field(default=None, ge=1)
    source_url: str
    source_approved: Literal[True] = True
    status: ProjectVideoProcedureStatus
    procedure: Procedure | None = None
    provider: Literal["vertex_ai", "gemini_api"] | None = None
    requested_model: str | None = None
    model_version: str | None = None
    elapsed_seconds: float | None = Field(default=None, ge=0)
    usage: GeminiUsage = Field(default_factory=GeminiUsage)
    cloud_calls_made: int = Field(default=0, ge=0, le=1)
    media_resolution: Literal["low"] = "low"
    raw_response_retained: Literal[False] = False
    failure_code: str | None = Field(default=None, max_length=80)
    failure_message: str | None = Field(default=None, max_length=240)
    review_notes: str | None = Field(default=None, max_length=2000)
    created_at: datetime
    reviewed_at: datetime | None = None
