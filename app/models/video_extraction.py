"""Contracts for the first controlled instructional-video experiment."""

from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.models.procedure import Procedure


class VideoExtractionRequest(BaseModel):
    """One approved public YouTube source to analyze with a cloud model."""

    video_url: HttpUrl
    task_hint: str | None = Field(default=None, max_length=500)
    output_language: Literal["es", "en"] = "es"
    acknowledge_cloud_cost: Literal[True]

    @field_validator("video_url")
    @classmethod
    def require_public_youtube_url(cls, value: HttpUrl) -> HttpUrl:
        """Restrict the first experiment to supported public YouTube URLs."""
        host = (urlparse(str(value)).hostname or "").lower()
        allowed_hosts = {
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be",
        }
        if host not in allowed_hosts:
            raise ValueError("The first video experiment accepts only YouTube URLs.")
        return value


class GeminiUsage(BaseModel):
    """Provider-reported token use for one completed cloud call."""

    prompt_tokens: int | None = Field(default=None, ge=0)
    candidate_tokens: int | None = Field(default=None, ge=0)
    thoughts_tokens: int | None = Field(default=None, ge=0)
    cached_content_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class VideoExtractionResult(BaseModel):
    """Structured evidence returned by the controlled provider experiment."""

    source_url: str
    procedure: Procedure
    provider: Literal["vertex_ai", "gemini_api"]
    requested_model: str
    model_version: str | None = None
    elapsed_seconds: float = Field(ge=0)
    usage: GeminiUsage
    cloud_calls_made: int = Field(default=1, ge=1, le=1)
    media_resolution: Literal["low"] = "low"
    raw_response_retained: Literal[False] = False
