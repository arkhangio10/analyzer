"""Gemini provider boundary for multimodal procedural extraction."""

from collections.abc import Callable
import json
import re
from time import perf_counter
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.models.motion_analysis import MotionAnalysisCall, ObservedMotionReport
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

    def __init__(
        self,
        failure_code: str = "provider_error",
        *,
        http_status: int | None = None,
        provider_status: str | None = None,
        requested_model: str | None = None,
    ) -> None:
        super().__init__(
            f"Gemini could not process the approved video ({failure_code})."
        )
        self.failure_code = failure_code
        self.http_status = http_status
        self.provider_status = provider_status
        self.requested_model = requested_model


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
        requested_model = self._settings.google_genai_youtube_model
        started = perf_counter()
        try:
            response = await client.aio.models.generate_content(
                model=requested_model,
                contents=[
                    types.Part.from_uri(
                        file_uri=self._provider_video_url(str(request.video_url)),
                        mime_type="video/mp4",
                    ),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=(
                        self._settings.google_genai_youtube_max_output_tokens
                    ),
                    response_mime_type="application/json",
                    response_schema=Procedure,
                    media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                ),
            )
        except Exception as error:
            raise GeminiProviderError(
                self._classify_provider_error(error),
                http_status=self._provider_http_status(error),
                provider_status=self._provider_status(error),
                requested_model=requested_model,
            ) from error
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
            requested_model=requested_model,
            model_version=getattr(response, "model_version", None),
            elapsed_seconds=round(elapsed_seconds, 3),
            usage=self._extract_usage(getattr(response, "usage_metadata", None)),
        )

    async def analyze_motion(
        self,
        *,
        video_url: str,
        frames_per_second: float,
        window_start_seconds: float,
        window_end_seconds: float,
        output_language: str = "es",
    ) -> MotionAnalysisCall:
        """Sample one approved video for movement rather than instruction.

        The procedure pass reads a video at the provider's default cadence and
        returns prose. This pass pins an explicit frame rate and a bounded
        window so joint angles can be estimated densely enough to be compared
        over time. The window is bounded on purpose: frame rate multiplies
        cost, so a caller always states how much video is sampled.
        """
        client = self._create_client()
        requested_model = self._settings.google_genai_youtube_model
        started = perf_counter()
        try:
            response = await client.aio.models.generate_content(
                model=requested_model,
                contents=[
                    types.Part(
                        file_data=types.FileData(
                            file_uri=self._provider_video_url(video_url),
                            mime_type="video/mp4",
                        ),
                        video_metadata=types.VideoMetadata(
                            fps=frames_per_second,
                            start_offset=f"{window_start_seconds:.0f}s",
                            end_offset=f"{window_end_seconds:.0f}s",
                        ),
                    ),
                    self._build_motion_prompt(
                        frames_per_second=frames_per_second,
                        window_start_seconds=window_start_seconds,
                        window_end_seconds=window_end_seconds,
                        output_language=output_language,
                    ),
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=(
                        self._settings.google_genai_motion_max_output_tokens
                    ),
                    response_mime_type="application/json",
                    response_schema=ObservedMotionReport,
                    media_resolution=types.MediaResolution.MEDIA_RESOLUTION_MEDIUM,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                ),
            )
        except Exception as error:
            raise GeminiProviderError(
                self._classify_provider_error(error),
                http_status=self._provider_http_status(error),
                provider_status=self._provider_status(error),
                requested_model=requested_model,
            ) from error
        elapsed_seconds = perf_counter() - started

        return MotionAnalysisCall(
            report=self._parse_motion_report(response),
            provider=(
                "vertex_ai"
                if self._settings.google_genai_use_vertexai
                else "gemini_api"
            ),
            requested_model=requested_model,
            model_version=getattr(response, "model_version", None),
            elapsed_seconds=round(elapsed_seconds, 3),
            usage=self._extract_usage(getattr(response, "usage_metadata", None)),
        )

    @staticmethod
    def _build_motion_prompt(
        *,
        frames_per_second: float,
        window_start_seconds: float,
        window_end_seconds: float,
        output_language: str,
    ) -> str:
        language = "Spanish" if output_language == "es" else "English"
        return (
            "You are measuring movement, not explaining it. This video is "
            f"sampled at {frames_per_second:g} frames per second between "
            f"{window_start_seconds:g}s and {window_end_seconds:g}s. "
            "For each sampled instant, estimate the angle of every joint you "
            "can actually see on the moving subject, in degrees, where 0 is "
            "the neutral standing pose and flexion is positive. "
            "Report timestamps in seconds from the start of the video. "
            "Never interpolate, never repeat a previous value to fill a gap, "
            "and never report a joint you cannot see: omit it instead, and "
            "say so in uncertainties. Mark every sample with how clearly the "
            "joint was visible and how confident the estimate is. "
            "Segment the movement into its natural phases with start and end "
            "times. State plainly what the camera angle, occlusion, clothing, "
            "or sampling rate prevented you from measuring. "
            "Each sample is one row: t is the time in seconds, j is the joint "
            "written as side.name such as left.knee, a is the angle in "
            "degrees, c is your confidence from 0 to 1, and v is clear, "
            "partial, or occluded. Emit rows compactly and spend the "
            "response on samples rather than prose. "
            f"Write joint identities in lowercase English. Write phase "
            f"names, descriptions, and uncertainties in {language}."
        )

    @staticmethod
    def _parse_motion_report(response: Any) -> ObservedMotionReport:
        """Return the report, salvaging one that was cut off mid-sample.

        A dense analysis can exhaust the output budget partway through the
        sample array. That response was still paid for and the samples before
        the cut are still real, so the complete prefix is recovered instead of
        discarded. The salvage records itself as an uncertainty so a reader
        can never mistake a truncated analysis for a complete one.
        """
        text: str | None = None
        try:
            parsed = getattr(response, "parsed", None)
            if isinstance(parsed, ObservedMotionReport):
                return parsed
            if parsed is not None:
                return ObservedMotionReport.model_validate(parsed)
            text = getattr(response, "text", None)
            if text:
                return ObservedMotionReport.model_validate_json(text)
        except (ValidationError, TypeError, ValueError) as error:
            salvaged = (
                GeminiService._salvage_motion_report(text) if text else None
            )
            if salvaged is not None:
                return salvaged
            raise GeminiResponseError(
                "Gemini returned invalid or incomplete motion samples; no raw "
                "response was retained."
            ) from error
        raise GeminiResponseError(
            "Gemini returned no structured motion samples; no result was retained."
        )

    @staticmethod
    def _salvage_motion_report(text: str) -> ObservedMotionReport | None:
        """Rebuild a report from the complete prefix of a truncated response."""
        samples = GeminiService._complete_objects(text, "samples")
        if not samples:
            return None
        payload: dict[str, Any] = {
            "subject_kind": GeminiService._scalar_field(text, "subject_kind") or "",
            "kinematic_chain": (
                GeminiService._scalar_field(text, "kinematic_chain") or ""
            ),
            "phases": GeminiService._complete_objects(text, "phases"),
            "samples": samples,
            "uncertainties": [
                "The provider response reached its output limit and was cut "
                f"off after {len(samples)} samples. Everything here arrived "
                "complete before the cut; nothing was reconstructed."
            ],
        }
        try:
            return ObservedMotionReport.model_validate(payload)
        except ValidationError:
            return None

    @staticmethod
    def _scalar_field(text: str, name: str) -> str | None:
        """Read one top-level JSON string field out of a partial document."""
        pattern = '"' + name + r'"\s*:\s*"((?:[^"\\]|\\.)*)"'
        match = re.search(pattern, text)
        return match.group(1) if match else None

    @staticmethod
    def _complete_objects(text: str, name: str) -> list[dict[str, Any]]:
        """Collect the balanced JSON objects of one array, ignoring a cut tail."""
        marker = re.search('"' + name + r'"\s*:\s*\[', text)
        if not marker:
            return []
        items: list[dict[str, Any]] = []
        index = marker.end()
        length = len(text)
        separators = set(" \t\r\n,")
        while index < length:
            while index < length and text[index] in separators:
                index += 1
            if index >= length or text[index] != "{":
                break
            depth = 0
            in_string = False
            escaped = False
            start = index
            closed = False
            while index < length:
                character = text[index]
                if in_string:
                    if escaped:
                        escaped = False
                    elif character == "\\":
                        escaped = True
                    elif character == chr(34):
                        in_string = False
                elif character == chr(34):
                    in_string = True
                elif character == "{":
                    depth += 1
                elif character == "}":
                    depth -= 1
                    if depth == 0:
                        index += 1
                        closed = True
                        break
                index += 1
            if not closed:
                break
            try:
                items.append(json.loads(text[start:index]))
            except json.JSONDecodeError:
                break
        return items

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
            "timestamps and concise evidence for each step. Return no more than "
            "12 ordered steps, use at most two timestamps per step, and keep each "
            "action and evidence statement brief. Merge repeated demonstrations "
            "of the same action. Exclude promotions, subscriptions, website visits, "
            "and other calls to action that are not part of the demonstrated task. "
            "Make uncertainty and exceptions explicit. "
            f"{task_hint}Return all natural-language fields in {language}."
        )

    @staticmethod
    def _parse_procedure(response: Any) -> Procedure:
        try:
            parsed = getattr(response, "parsed", None)
            if isinstance(parsed, Procedure):
                return parsed
            if parsed is not None:
                return Procedure.model_validate(parsed)
            text = getattr(response, "text", None)
            if text:
                return Procedure.model_validate_json(text)
        except (ValidationError, TypeError, ValueError) as error:
            raise GeminiResponseError(
                "Gemini returned invalid or incomplete structured procedure data; "
                "no raw response was retained."
            ) from error
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
        code = GeminiService._provider_http_status(error)
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
    def _provider_http_status(error: Exception) -> int | None:
        """Return only a safe numeric provider status code."""
        value = getattr(error, "code", None) or getattr(error, "status_code", None)
        try:
            code = int(value)
        except (TypeError, ValueError):
            return None
        return code if 100 <= code <= 599 else None

    @staticmethod
    def _provider_status(error: Exception) -> str | None:
        """Retain a bounded provider status label without raw error details."""
        value = str(getattr(error, "status", "") or "").upper()
        if re.fullmatch(r"[A-Z][A-Z0-9_]{0,39}", value):
            return value
        return None

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
