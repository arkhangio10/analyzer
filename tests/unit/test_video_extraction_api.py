"""API safety-gate tests for the first real video experiment."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_video_extraction_requires_cost_acknowledgement() -> None:
    response = client.post(
        "/api/experiments/video/extract",
        json={
            "video_url": "https://www.youtube.com/watch?v=example",
            "acknowledge_cloud_cost": False,
        },
    )

    assert response.status_code == 422


def test_video_extraction_rejects_non_youtube_sources() -> None:
    response = client.post(
        "/api/experiments/video/extract",
        json={
            "video_url": "https://example.com/video.mp4",
            "acknowledge_cloud_cost": True,
        },
    )

    assert response.status_code == 422


def test_video_extraction_is_disabled_by_default() -> None:
    response = client.post(
        "/api/experiments/video/extract",
        json={
            "video_url": "https://youtu.be/example",
            "acknowledge_cloud_cost": True,
        },
    )

    assert response.status_code == 503
    assert "Gemini calls are disabled" in response.json()["detail"]

