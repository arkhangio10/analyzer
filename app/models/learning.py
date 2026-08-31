"""Cross-source learning and protected evaluation contracts."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.procedure import Procedure


class ProcedureEvidence(BaseModel):
    """Procedure extracted from an explicitly approved source."""

    source_id: str = Field(min_length=1, max_length=200)
    approved: Literal[True]
    procedure: Procedure


class ReconciliationRequest(BaseModel):
    """Two or more independent procedures to compare."""

    task: str = Field(min_length=3, max_length=300)
    sources: list[ProcedureEvidence] = Field(min_length=2, max_length=10)


class ReconciliationResult(BaseModel):
    """Consensus procedure plus visible conflicts and uncertainty."""

    procedure: Procedure
    source_count: int = Field(ge=2)
    agreements: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    ready_for_practice: bool


class FrozenEvaluationRequest(BaseModel):
    """Candidate output for a protected case whose answer is server-side."""

    evaluation_id: str = Field(min_length=1, max_length=120)
    skill_id: str = Field(min_length=1, max_length=120)
    case_id: str = Field(min_length=1, max_length=120)
    actual_output: dict[str, Any]


class FrozenEvaluationResult(BaseModel):
    """Evaluation evidence that does not reveal the protected answer."""

    evaluation_id: str
    skill_id: str
    case_id: str
    passed: bool
    score: float = Field(ge=0, le=1)
    checked_fields: list[str]
    failures: list[str] = Field(default_factory=list)
    expected_output_disclosed: Literal[False] = False
    expected_authored_by: Literal["human", "specification", "generated"]
    counts_as_external_validation: bool


class ReconciledSource(BaseModel):
    """One approved extraction that fed a reconciliation."""

    extraction_id: str = Field(min_length=1, max_length=120)
    procedure_version: int | None = Field(default=None, ge=1)
    source_url: str = Field(min_length=1, max_length=500)
    step_count: int = Field(ge=0)


class ProjectReconciliation(BaseModel):
    """A project's reconciliation, with how independent its sources really are.

    Agreement between two readings of the same video is not confirmation: it
    says the model repeated itself, not that the procedure is right. So the
    number of distinct sources is reported alongside the result, and
    `is_cross_source` is false until two different videos have been approved.
    """

    project_id: str = Field(min_length=1)
    result: ReconciliationResult
    sources: list[ReconciledSource] = Field(default_factory=list, max_length=10)
    distinct_source_count: int = Field(ge=0)
    is_cross_source: bool
    independence_note: str = Field(min_length=1, max_length=400)
