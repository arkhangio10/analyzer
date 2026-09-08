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
    # Motion analysis returns hundreds of joint samples, so its ceiling is
    # separate from procedure extraction: the response is bounded by output
    # tokens long before it is bounded by frame rate.
    google_genai_motion_max_output_tokens: int = Field(
        default=16384,
        ge=1024,
        le=32768,
    )
    youtube_search_enabled: bool = False
    youtube_api_key: str | None = None
    computer_execution_boundary: Literal[
        "managed_local_directory",
        "application_container",
    ] = "managed_local_directory"
    computer_browser_enabled: bool = False
    # Evidence storage. Off by default like every other outbound integration:
    # the application must run and pass its tests on a machine that has no
    # ClickHouse, and fall back to reporting that evidence is not durable.
    clickhouse_enabled: bool = False
    clickhouse_host: str | None = None
    clickhouse_port: int = Field(default=8443, ge=1, le=65535)
    clickhouse_user: str = "default"
    clickhouse_password: str | None = None
    clickhouse_database: str = "default"
    clickhouse_secure: bool = True

    firestore_database: str | None = None
    gcs_bucket: str | None = None
    data_dir: str = "data"
    frozen_cases_dir: str | None = None
    app_env: str = "development"
    log_level: str = "INFO"

    # Cloud Run sets K_SERVICE in every container it starts. It is read here
    # only to tell a container that keeps nothing from a machine that does: a
    # writable directory on Cloud Run accepts records and loses them at the
    # next revision or scale event, so durability reported from the filesystem
    # alone would be a lie there.
    k_service: str | None = None

    # Required by the endpoints that reach a provider once provider calls are
    # enabled. The QC console never needs it: reading stored evidence and
    # recomputing a verdict from stored samples costs nothing.
    spend_token: str | None = None

    # A ceiling the application enforces on itself, in the operator's own
    # currency. A cloud budget cannot do this: it notifies after the fact and
    # the spending continues. Unset means no ceiling.
    #
    # The prices are per million tokens and have no default on purpose. A
    # guessed price produces a ceiling that is wrong in an unknown direction
    # and reads as protection anyway, so a ceiling set without them makes the
    # paid endpoints refuse. Copy the current numbers from the provider's
    # pricing page for the model in GOOGLE_GENAI_YOUTUBE_MODEL; they change.
    # An exported agent runs this same application with a baked-in skill and
    # no provider. AGENT_MODE switches the root page to the agent's own
    # interface and SKILL_PATH names what it knows.
    agent_mode: bool = False
    skill_path: str | None = None

    spend_currency: str = "PEN"
    spend_ceiling: float | None = Field(default=None, ge=0)
    price_per_million_input_tokens: float | None = Field(default=None, ge=0)
    price_per_million_output_tokens: float | None = Field(default=None, ge=0)

    @property
    def is_stateless_container(self) -> bool:
        """Report whether this process runs where local disk does not survive."""
        return bool(self.k_service)

    @property
    def records_survive_restart(self) -> bool:
        """Report whether written records outlive this container."""
        if self.is_stateless_container:
            return bool(self.gcs_bucket)
        return True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings without exposing secret values."""
    return Settings()
