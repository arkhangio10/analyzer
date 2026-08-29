"""Contracts for automatic reference discovery and user approval."""

from typing import Literal

from pydantic import BaseModel, Field


class SourceSearchRequest(BaseModel):
    """Bounded YouTube discovery request authorized by a user action."""

    query: str = Field(min_length=3, max_length=300)
    language: Literal["es", "en"] = "es"
    max_results: int = Field(default=3, ge=1, le=5)
    acknowledge_search_quota: Literal[True]


class VideoCandidate(BaseModel):
    """Reviewable reference returned by YouTube Data API."""

    video_id: str
    url: str
    title: str
    channel: str
    published_at: str | None = None
    summary: str
    thumbnail_url: str | None = None


class SourceSearchResult(BaseModel):
    """Candidate set that remains unapproved until a second user action."""

    search_id: str
    query: str
    candidates: list[VideoCandidate]
    provider: Literal["youtube_data_api_v3"] = "youtube_data_api_v3"
    search_calls_made: Literal[1] = 1
    approval_required: Literal[True] = True


class SourceApprovalRequest(BaseModel):
    """Explicit candidate selection for a completed discovery request."""

    video_ids: list[str] = Field(min_length=1, max_length=5)


class SourceApprovalResult(BaseModel):
    """References approved for later video analysis."""

    search_id: str
    approved_sources: list[VideoCandidate]
    analysis_started: Literal[False] = False
