"""Environment-backed application settings."""

from functools import lru_cache

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables or a local .env file."""

    google_api_key: str | None = None
    google_cloud_project: str | None = None
    google_cloud_location: str | None = None
    google_genai_enabled: bool = False
    google_genai_use_vertexai: bool = False
    google_genai_model: str = "gemini-3.5-flash-lite"
    google_genai_youtube_model: str = "gemini-2.5-flash-lite"
    google_genai_max_output_tokens: int = Field(default=4096, ge=256, le=8192)
    google_genai_youtube_max_output_tokens: int = Field(
        default=8192,
        ge=256,
        le=16384,
    )
    youtube_search_enabled: bool = False
    youtube_api_key: str | None = None
    computer_execution_boundary: Literal[
        "managed_local_directory",
        "application_container",
    ] = "managed_local_directory"
    computer_browser_enabled: bool = False
    firestore_database: str | None = None
    gcs_bucket: str | None = None
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings without exposing secret values."""
    return Settings()
