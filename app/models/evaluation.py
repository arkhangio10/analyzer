"""Evaluation-result data contracts."""

from typing import Any

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Transparent comparison of actual and externally anchored results."""

    evaluation_id: str = Field(min_length=1)
    skill_id: str = Field(min_length=1)
    passed: bool
    actual_output: dict[str, Any] = Field(default_factory=dict)
    expected_output: dict[str, Any] = Field(default_factory=dict)
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    failures: list[str] = Field(default_factory=list)
    notes: str | None = None
