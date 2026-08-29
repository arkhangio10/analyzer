"""Task-understanding data contracts."""

from pydantic import BaseModel, Field


class TaskDefinition(BaseModel):
    """The explicit contract APRENDIZ must understand before learning."""

    task_name: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    expected_inputs: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    tools_involved: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    known_exceptions: list[str] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)
    is_sufficiently_clear: bool = False
