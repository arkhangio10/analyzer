"""Learned-skill data contracts."""

from pydantic import BaseModel, Field

from app.models.procedure import Procedure
from app.models.training import TrainingExample


class Skill(BaseModel):
    """Versioned procedural knowledge used by an executor agent."""

    skill_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    version: int = Field(default=1, ge=1)
    objective: str = Field(min_length=1)
    inputs: dict[str, str] = Field(default_factory=dict)
    outputs: dict[str, str] = Field(default_factory=dict)
    procedure: Procedure
    examples: list[TrainingExample] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    evaluation: dict[str, object] = Field(default_factory=dict)
