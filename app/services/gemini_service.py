"""Gemini provider boundary for multimodal procedural extraction."""

from collections.abc import Callable
from time import perf_counter
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from google import genai
from google.genai import types

from app.core.config import Settings, get_settings
from app.models.procedure import Procedure
from app.models.video_extraction import (
    GeminiUsage,
    VideoExtractionRequest,
    VideoExtractionResult,
)


class GeminiConfigurationError(RuntimeError):
    """Raised before a cloud call when provider configuration is incomplete."""


class GeminiResponseError(RuntimeError):
    """Raised when the provider does not return the required typed procedure."""


class GeminiProviderError(RuntimeError):
    """Raised when the provider call fails without exposing provider internals."""

    def __init__(self, failure_code: str = "provider_error") -> None:
        super().__init__(
            f"Gemini could not process the approved video ({failure_code})."
        )
        self.failure_code = failure_code


class GeminiService:
    """Analyze one approved YouTube video through a controlled provider call."""

    def __init__(
        self,
        settings: Settings | None = None,
        client_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._client_factory = client_factory or genai.Client

    def _create_client(self) -> Any:
        settings = self._settings
        if not settings.google_genai_enabled:
            raise GeminiConfigurationError(
                "Gemini calls are disabled. Set GOOGLE_GENAI_ENABLED=true explicitly."
            )

        if settings.google_genai_use_vertexai:
            if not settings.google_cloud_project or not settings.google_cloud_location:
                raise GeminiConfigurationError(
                    "Vertex AI requires GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION."
                )
            return self._client_factory(
                vertexai=True,
                project=settings.google_cloud_project,
                location=settings.google_cloud_location,
                http_options=types.HttpOptions(api_version="v1"),
            )

        if not settings.google_api_key:
            raise GeminiConfigurationError(
                "The Gemini Developer API requires GOOGLE_API_KEY."
            )
        return self._client_factory(api_key=settings.google_api_key)

    async def extract_procedure(
        self,
        request: VideoExtractionRequest,
    ) -> VideoExtractionResult:
        """Extract typed procedural memory from one approved public video."""
        client = self._create_client()
        prompt = self._build_prompt(request)
        started = perf_counter()
        try:
            response = await client.aio.models.generate_content(
                model=self._settings.google_genai_model,
                contents=[
                    types.Part.from_uri(
                        file_uri=self._provider_video_url(str(request.video_url)),
                        mime_type="video/mp4",
                    ),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=self._settings.google_genai_max_output_tokens,
                    response_mime_type="application/json",
                    response_schema=Procedure,
                    media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                ),
            )
        except Exception as error:
            raise GeminiProviderError(self._classify_provider_error(error)) from error
        elapsed_seconds = perf_counter() - started
        procedure = self._parse_procedure(response)

        return VideoExtractionResult(
            source_url=str(request.video_url),
            procedure=procedure,
            provider=(
                "vertex_ai"
                if self._settings.google_genai_use_vertexai
                else "gemini_api"
            ),
            requested_model=self._settings.google_genai_model,
            model_version=getattr(response, "model_version", None),
            elapsed_seconds=round(elapsed_seconds, 3),
            usage=self._extract_usage(getattr(response, "usage_metadata", None)),
        )

    @staticmethod
    def _build_prompt(request: VideoExtractionRequest) -> str:
        language = "Spanish" if request.output_language == "es" else "English"
        task_hint = (
            f"The user's task hint is: {request.task_hint}\n"
            if request.task_hint
            else ""
        )
        return (
            "Analyze both the visual stream and audio of this instructional video. "
            "Extract only procedures supported by the demonstration. Do not invent "
            "missing steps, rules, results, or examples. Record relevant MM:SS "
            "timestamps and concise evidence for each step. Make uncertainty and "
            "exceptions explicit. "
            f"{task_hint}Return all natural-language fields in {language}."
        )

    @staticmethod
    def _parse_procedure(response: Any) -> Procedure:
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, Procedure):
            return parsed
        if parsed is not None:
            return Procedure.model_validate(parsed)
        text = getattr(response, "text", None)
        if text:
            return Procedure.model_validate_json(text)
        raise GeminiResponseError(
            "Gemini returned no structured procedure; no result was retained."
        )

    @staticmethod
    def _extract_usage(metadata: Any) -> GeminiUsage:
        if metadata is None:
            return GeminiUsage()
        return GeminiUsage(
            prompt_tokens=getattr(metadata, "prompt_token_count", None),
            candidate_tokens=getattr(metadata, "candidates_token_count", None),
            thoughts_tokens=getattr(metadata, "thoughts_token_count", None),
            cached_content_tokens=getattr(
                metadata, "cached_content_token_count", None
            ),
            total_tokens=getattr(metadata, "total_token_count", None),
        )

    @staticmethod
    def _classify_provider_error(error: Exception) -> str:
        """Map provider details to a stable category without exposing raw text."""
        message = str(error).casefold()
        code = getattr(error, "code", None) or getattr(error, "status_code", None)
        if code == 429 or "quota" in message or "resource_exhausted" in message:
            return "quota_exceeded"
        if code == 403 or "permission" in message or "permission_denied" in message:
            return "permission_denied"
        if "youtube" in message and any(
            marker in message
            for marker in ("invalid", "unsupported", "not accessible", "cannot access")
        ):
            return "youtube_source_rejected"
        if "model" in message and any(
            marker in message for marker in ("not found", "unsupported", "unavailable")
        ):
            return "model_unavailable"
        if "safety" in message or "blocked" in message:
            return "safety_blocked"
        if code == 400 or "invalid_argument" in message:
            return "invalid_request"
        if code in {500, 502, 503, 504} or "unavailable" in message:
            return "provider_unavailable"
        return "provider_error"

    @staticmethod
    def _provider_video_url(source_url: str) -> str:
        """Canonicalize YouTube share URLs while preserving the source record."""
        parsed = urlparse(source_url)
        host = (parsed.hostname or "").casefold()
        video_id: str | None = None
        if host == "youtu.be":
            video_id = parsed.path.strip("/").split("/", maxsplit=1)[0] or None
        elif host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        if not video_id:
            return source_url
        return urlunparse(
            ("https", "www.youtube.com", "/watch", "", urlencode({"v": video_id}), "")
        )
