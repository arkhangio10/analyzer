"""Contracts for video a person supplies from their own machine.

An uploaded file is the one source APRENDIZ holds that nobody else has seen.
Two guarantees are written into the type rather than left to a comment:

- `stored_locally` is permanently true and `sent_to_provider` is permanently
  false. Nothing in this codebase may hand an uploaded file to a cloud model,
  because the person who supplied it has not agreed to that.
- `analysis_available` is permanently false. Extraction today accepts only a
  public YouTube URL, so an upload can be kept, listed, and verified by its
  hash, but it cannot yet be turned into a procedure. Saying so in the contract
  keeps the interface from implying a capability that does not exist.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ALLOWED_VIDEO_TYPES: dict[str, str] = {
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/webm": ".webm",
    "video/x-matroska": ".mkv",
}

ALLOWED_EXTENSIONS: frozenset[str] = frozenset(ALLOWED_VIDEO_TYPES.values())


class UploadedVideoRecord(BaseModel):
    """One video kept on this machine, described by what can be verified."""

    upload_id: str = Field(min_length=1, max_length=120)
    project_id: str = Field(min_length=1, max_length=120)
    original_filename: str = Field(min_length=1, max_length=260)
    stored_filename: str = Field(min_length=1, max_length=160)
    content_type: str = Field(min_length=1, max_length=80)
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    created_at: datetime

    stored_locally: Literal[True] = True
    sent_to_provider: Literal[False] = False
    analysis_available: Literal[False] = False


class UploadedVideoList(BaseModel):
    """Every upload retained for one project, with the storage guarantees."""

    project_id: str = Field(min_length=1)
    uploads: list[UploadedVideoRecord] = Field(default_factory=list, max_length=200)
    total_bytes: int = Field(ge=0)
    max_upload_bytes: int = Field(ge=0)
    accepted_types: list[str] = Field(default_factory=list)
    storage_note: str = Field(min_length=1, max_length=400)
