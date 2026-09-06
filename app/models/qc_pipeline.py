"""Contracts for what the QC pipeline did, stage by stage.

The pipeline's output is not a procedure and not a judgement about a robot. It
is an account of which claims about a video were checked against stored
observations, which were not, and why. So every stage reports an outcome from a
closed set rather than a free-text status, and a stage that did nothing says
which of the several reasons applied: nobody approved the source, there was no
evidence to check, or the check itself failed.

`QcReport.proven` is deliberately narrow. It is true only when the audit
recomputed the verdict from stored samples and reached the same answer the
stored record claims. Anything else -- no evidence, no approval, a failure --
leaves it false, because the pipeline can then say what happened but cannot say
the metadata was observed.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class StageOutcome(StrEnum):
    """What one stage managed to do."""

    COMPLETED = "completed"
    BLOCKED_AWAITING_APPROVAL = "blocked_awaiting_approval"
    NO_EVIDENCE = "no_evidence"
    FAILED = "failed"


class StageReport(BaseModel):
    """One stage's account of itself."""

    stage: str = Field(min_length=1, max_length=60)
    outcome: StageOutcome
    detail: str = Field(min_length=1, max_length=400)
    cloud_calls_made: int = Field(default=0, ge=0)


class QcReport(BaseModel):
    """What the pipeline established about one extraction."""

    project_id: str = Field(min_length=1)
    extraction_id: str = Field(min_length=1)
    analysis_id: str | None = None
    source_url: str | None = None

    stages: list[StageReport] = Field(default_factory=list, max_length=20)
    approved: bool = False
    proven: bool = False
    claimed_verdict: str | None = None
    recomputed_verdict: str | None = None
    sql_verdict: str | None = None

    cloud_calls_made: int = Field(default=0, ge=0)
    created_at: datetime

    @property
    def blocked(self) -> bool:
        """Report whether the pipeline stopped short of checking anything."""
        return any(
            stage.outcome is StageOutcome.BLOCKED_AWAITING_APPROVAL
            for stage in self.stages
        )
