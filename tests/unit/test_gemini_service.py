"""Unit tests for the controlled Gemini provider boundary."""

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

from app.core.config import Settings
from app.models.procedure import Procedure, ProcedureStep
from app.models.video_extraction import VideoExtractionRequest
from app.services.gemini_service import (
    GeminiConfigurationError,
    GeminiProviderError,
    GeminiService,
)


def make_request() -> VideoExtractionRequest:
    return VideoExtractionRequest(
        video_url="https://www.youtube.com/watch?v=example",
        task_hint="Teach the demonstrated task.",
        output_language="en",
        acknowledge_cloud_cost=True,
    )


def make_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "google_genai_enabled": True,
        "google_genai_use_vertexai": True,
        "google_cloud_project": "test-project",
        "google_cloud_location": "global",
        "google_genai_model": "gemini-3.5-flash-lite",
        "google_genai_max_output_tokens": 1024,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


class FakeModels:
    def __init__(self, response: Any = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.request: dict[str, Any] | None = None

    async def generate_content(self, **kwargs: Any) -> Any:
        self.request = kwargs
        if self.error:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, models: FakeModels) -> None:
        self.aio = SimpleNamespace(models=models)


def test_extract_procedure_returns_usage_and_typed_result() -> None:
    procedure = Procedure(
        task="Paint a wall",
        objective="Apply an even coat.",
        steps=[
            ProcedureStep(
                step=1,
                action="Load the roller.",
                source_timestamps=["00:04"],
                evidence="The instructor coats the roller.",
            )
        ],
    )
    response = SimpleNamespace(
        parsed=procedure,
        model_version="gemini-test",
        usage_metadata=SimpleNamespace(
            prompt_token_count=120,
            candidates_token_count=30,
            thoughts_token_count=5,
            cached_content_token_count=0,
            total_token_count=155,
        ),
    )
    models = FakeModels(response=response)
    client_arguments: dict[str, Any] = {}

    def client_factory(**kwargs: Any) -> FakeClient:
        client_arguments.update(kwargs)
        return FakeClient(models)

    service = GeminiService(make_settings(), client_factory=client_factory)
    result = asyncio.run(service.extract_procedure(make_request()))

    assert result.procedure == procedure
    assert result.provider == "vertex_ai"
    assert result.cloud_calls_made == 1
    assert result.usage.total_tokens == 155
    assert result.raw_response_retained is False
    assert client_arguments["project"] == "test-project"
    assert models.request is not None
    assert models.request["model"] == "gemini-3.5-flash-lite"
    assert models.request["contents"][0].file_data.file_uri.startswith(
        "https://www.youtube.com/"
    )
    assert models.request["config"].max_output_tokens == 1024


def test_disabled_provider_fails_before_creating_client() -> None:
    def forbidden_client(**kwargs: Any) -> None:
        raise AssertionError(f"Client should not be created: {kwargs}")

    service = GeminiService(
        make_settings(google_genai_enabled=False),
        client_factory=forbidden_client,
    )

    with pytest.raises(GeminiConfigurationError):
        asyncio.run(service.extract_procedure(make_request()))


def test_provider_failure_is_sanitized() -> None:
    models = FakeModels(error=RuntimeError("provider detail that must stay private"))
    service = GeminiService(
        make_settings(),
        client_factory=lambda **kwargs: FakeClient(models),
    )

    with pytest.raises(
        GeminiProviderError,
        match="Gemini could not process the approved video",
    ):
        asyncio.run(service.extract_procedure(make_request()))


def test_provider_failure_is_classified_without_returning_raw_details() -> None:
    models = FakeModels(error=RuntimeError("429 RESOURCE_EXHAUSTED: private detail"))
    service = GeminiService(
        make_settings(),
        client_factory=lambda **kwargs: FakeClient(models),
    )

    with pytest.raises(GeminiProviderError) as captured:
        asyncio.run(service.extract_procedure(make_request()))

    assert captured.value.failure_code == "quota_exceeded"
    assert "private detail" not in str(captured.value)


def test_youtube_share_url_is_canonicalized_for_the_provider() -> None:
    result = GeminiService._provider_video_url(
        "https://youtu.be/-fD2TSL2s7I?si=private-share-value"
    )

    assert result == "https://www.youtube.com/watch?v=-fD2TSL2s7I"
    assert "private-share-value" not in result
