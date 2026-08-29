"""YouTube reference discovery without downloading video content."""

from html import unescape
from uuid import uuid4

import httpx

from app.core.config import Settings, get_settings
from app.models.source import (
    SourceApprovalResult,
    SourceSearchRequest,
    SourceSearchResult,
    VideoCandidate,
)


class YouTubeConfigurationError(RuntimeError):
    """Raised when automatic search has not been explicitly configured."""


class YouTubeProviderError(RuntimeError):
    """Raised when YouTube Data API rejects or cannot complete a request."""


class SourceSearchNotFoundError(LookupError):
    """Raised when an approval references an unknown search."""


class SourceSelectionError(ValueError):
    """Raised when approval includes a video outside the candidate set."""


class YouTubeService:
    """Search YouTube and retain candidates until the user approves them."""

    _SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._http_client = http_client
        self._searches: dict[str, SourceSearchResult] = {}

    async def search(self, request: SourceSearchRequest) -> SourceSearchResult:
        """Perform one bounded search call and return unapproved candidates."""
        if not self._settings.youtube_search_enabled:
            raise YouTubeConfigurationError(
                "Automatic YouTube search is disabled. Set YOUTUBE_SEARCH_ENABLED=true explicitly."
            )
        if not self._settings.youtube_api_key:
            raise YouTubeConfigurationError(
                "YOUTUBE_API_KEY is required when automatic search is enabled."
            )

        params = {
            "part": "snippet",
            "type": "video",
            "q": request.query.strip(),
            "maxResults": request.max_results,
            "relevanceLanguage": request.language,
            "safeSearch": "strict",
            "videoEmbeddable": "true",
            "key": self._settings.youtube_api_key,
        }
        owns_client = self._http_client is None
        client = self._http_client or httpx.AsyncClient(timeout=15.0)
        try:
            response = await client.get(self._SEARCH_URL, params=params)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise YouTubeProviderError(
                "YouTube reference search could not be completed."
            ) from error
        finally:
            if owns_client:
                await client.aclose()

        candidates = [
            self._candidate(item, request.language)
            for item in payload.get("items", [])
            if item.get("id", {}).get("videoId")
        ]
        result = SourceSearchResult(
            search_id=f"src_{uuid4().hex[:12]}",
            query=request.query.strip(),
            candidates=candidates,
        )
        self._searches[result.search_id] = result
        return result

    def approve(self, search_id: str, video_ids: list[str]) -> SourceApprovalResult:
        """Approve only candidates returned by the referenced search."""
        try:
            result = self._searches[search_id]
        except KeyError as error:
            raise SourceSearchNotFoundError(search_id) from error
        available = {candidate.video_id: candidate for candidate in result.candidates}
        unique_ids = list(dict.fromkeys(video_ids))
        if any(video_id not in available for video_id in unique_ids):
            raise SourceSelectionError(
                "Every approved video must belong to the referenced search."
            )
        return SourceApprovalResult(
            search_id=search_id,
            approved_sources=[available[video_id] for video_id in unique_ids],
        )

    @staticmethod
    def _candidate(item: dict, language: str) -> VideoCandidate:
        video_id = item["id"]["videoId"]
        snippet = item.get("snippet", {})
        description = " ".join(unescape(snippet.get("description", "")).split())
        if not description:
            description = (
                "Sin descripción pública; revisa el video antes de aprobarlo."
                if language == "es"
                else "No public description; review the video before approval."
            )
        thumbnails = snippet.get("thumbnails", {})
        thumbnail = thumbnails.get("medium") or thumbnails.get("default") or {}
        return VideoCandidate(
            video_id=video_id,
            url=f"https://www.youtube.com/watch?v={video_id}",
            title=unescape(snippet.get("title", "Untitled video")),
            channel=unescape(snippet.get("channelTitle", "Unknown channel")),
            published_at=snippet.get("publishedAt"),
            summary=description[:360],
            thumbnail_url=thumbnail.get("url"),
        )
