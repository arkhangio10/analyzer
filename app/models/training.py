"""Training-example data contracts."""

from typing import Any

from pydantic import BaseModel, Field


class TrainingExample(BaseModel):
    """An instructor-grounded, generated, or frozen example case."""

    example_id: str = Field(min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    expected_outputs: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None
    difficulty_level: int = Field(default=0, ge=0, le=5)
    is_frozen: bool = False
