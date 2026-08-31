"""Contracts for the history of one project's procedural memory.

Every extraction produces an immutable version. Keeping them is only half the
point: a person needs to see what actually changed between two of them, because
a second cloud call that quietly rewrites a reviewed step is exactly the kind of
drift this project exists to make visible.

A diff here is descriptive, never corrective. It reports what differs and never
merges, resolves, or picks a winner.
"""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.models.project_video_procedure import ProjectVideoProcedureStatus


class StepChangeKind(StrEnum):
    """What happened to one step between two versions."""

    UNCHANGED = "unchanged"
    CHANGED = "changed"
    ADDED = "added"
    REMOVED = "removed"


class ProcedureVersionSummary(BaseModel):
    """One retained version, described without opening the whole procedure."""

    extraction_id: str = Field(min_length=1)
    procedure_version: int | None = Field(default=None, ge=1)
    status: ProjectVideoProcedureStatus
    source_url: str = Field(min_length=1)
    task: str | None = Field(default=None, max_length=300)
    step_count: int = Field(ge=0)
    cloud_calls_made: int = Field(ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    created_at: datetime
    reviewed_at: datetime | None = None


class StepDifference(BaseModel):
    """One step as it stands in each of two versions."""

    step: int = Field(ge=1)
    kind: StepChangeKind
    before: str | None = Field(default=None, max_length=2000)
    after: str | None = Field(default=None, max_length=2000)
    before_timestamps: list[str] = Field(default_factory=list, max_length=20)
    after_timestamps: list[str] = Field(default_factory=list, max_length=20)


class ListDifference(BaseModel):
    """What one list of statements gained and lost between two versions."""

    field: str = Field(min_length=1, max_length=60)
    added: list[str] = Field(default_factory=list, max_length=60)
    removed: list[str] = Field(default_factory=list, max_length=60)


class ProcedureVersionDiff(BaseModel):
    """The difference between two retained versions of one procedure."""

    project_id: str = Field(min_length=1)
    from_extraction_id: str = Field(min_length=1)
    to_extraction_id: str = Field(min_length=1)
    from_version: int | None = Field(default=None, ge=1)
    to_version: int | None = Field(default=None, ge=1)
    same_source: bool
    from_source_url: str = Field(min_length=1)
    to_source_url: str = Field(min_length=1)
    steps: list[StepDifference] = Field(default_factory=list, max_length=200)
    added_step_count: int = Field(ge=0)
    removed_step_count: int = Field(ge=0)
    changed_step_count: int = Field(ge=0)
    unchanged_step_count: int = Field(ge=0)
    lists: list[ListDifference] = Field(default_factory=list, max_length=12)
    has_changes: bool
    is_advisory: Literal[True] = True


class ProcedureHistory(BaseModel):
    """Every retained version for one project, newest last."""

    project_id: str = Field(min_length=1)
    versions: list[ProcedureVersionSummary] = Field(
        default_factory=list,
        max_length=200,
    )
    total_cloud_calls: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    latest_diff: ProcedureVersionDiff | None = None
