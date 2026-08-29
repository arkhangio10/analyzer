"""Structured procedural-memory contracts."""

from pydantic import BaseModel, Field


class ProcedureStep(BaseModel):
    """One ordered and inspectable action in a procedure."""

    step: int = Field(ge=1)
    action: str = Field(min_length=1)
    condition: str | None = None
    expected_result: str | None = None
    source_timestamps: list[str] = Field(default_factory=list)
    evidence: str | None = None


class Procedure(BaseModel):
    """A procedure extracted from one or more demonstrations."""

    task: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    steps: list[ProcedureStep] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
