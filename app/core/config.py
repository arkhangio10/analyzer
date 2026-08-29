"""Environment-backed application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables or a local .env file."""

    google_api_key: str | None = None
    google_cloud_project: str | None = None
    google_cloud_location: str | None = None
    google_genai_use_vertexai: bool = False
    firestore_database: str | None = None
    gcs_bucket: str | None = None
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings without exposing secret values."""
    return Settings()
