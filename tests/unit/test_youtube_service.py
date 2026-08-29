"""Tests for guarded YouTube discovery and source approval."""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.models.source import SourceSearchRequest
from app.services.youtube_service import (
    SourceSelectionError,
    YouTubeConfigurationError,
    YouTubeService,
)


client = TestClient(app)


def _youtube_response(request: httpx.Request) -> httpx.Response:
    assert request.url.params["part"] == "snippet"
    assert request.url.params["type"] == "video"
    assert request.url.params["safeSearch"] == "strict"
    assert request.url.params["maxResults"] == "3"
    assert request.url.params["key"] == "test-key"
    return httpx.Response(
        200,
        json={
            "items": [
                {
                    "id": {"videoId": "dog-run-01"},
                    "snippet": {
                        "title": "Dog &amp; robot gait reference",
                        "description": "Side view of a dog running at a steady pace.",
                        "channelTitle": "Motion Lab",
                        "publishedAt": "2026-08-01T00:00:00Z",
                        "thumbnails": {
                            "medium": {"url": "https://img.example/video.jpg"}
                        },
                    },
                }
            ]
        },
        request=request,
    )


def test_search_returns_unapproved_candidates_and_approval_is_explicit() -> None:
    async def exercise() -> None:
        transport = httpx.MockTransport(_youtube_response)
        async with httpx.AsyncClient(transport=transport) as http_client:
            service = YouTubeService(
                settings=Settings(
                    youtube_search_enabled=True,
                    youtube_api_key="test-key",
                ),
                http_client=http_client,
            )
            result = await service.search(
                SourceSearchRequest(
                    query="dog running biomechanics",
                    language="en",
                    acknowledge_search_quota=True,
                )
            )

            assert result.approval_required is True
            assert result.search_calls_made == 1
            assert result.candidates[0].title == "Dog & robot gait reference"

            approval = service.approve(result.search_id, ["dog-run-01"])
            assert approval.analysis_started is False
            assert approval.approved_sources[0].video_id == "dog-run-01"

    asyncio.run(exercise())


def test_search_is_disabled_without_explicit_configuration() -> None:
    service = YouTubeService(settings=Settings(youtube_search_enabled=False))

    with pytest.raises(YouTubeConfigurationError):
        asyncio.run(
            service.search(
                SourceSearchRequest(
                    query="robot painting demonstration",
                    acknowledge_search_quota=True,
                )
            )
        )


def test_approval_rejects_video_outside_candidate_set() -> None:
    async def exercise() -> None:
        transport = httpx.MockTransport(_youtube_response)
        async with httpx.AsyncClient(transport=transport) as http_client:
            service = YouTubeService(
                settings=Settings(
                    youtube_search_enabled=True,
                    youtube_api_key="test-key",
                ),
                http_client=http_client,
            )
            result = await service.search(
                SourceSearchRequest(
                    query="dog running biomechanics",
                    acknowledge_search_quota=True,
                )
            )

            with pytest.raises(SourceSelectionError):
                service.approve(result.search_id, ["not-returned"])

    asyncio.run(exercise())


def test_search_endpoint_is_guarded_by_default() -> None:
    response = client.post(
        "/api/sources/search",
        json={
            "query": "dog running biomechanics",
            "language": "en",
            "acknowledge_search_quota": True,
        },
    )

    assert response.status_code == 503
