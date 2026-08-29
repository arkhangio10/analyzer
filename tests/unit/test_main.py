"""Smoke tests for the minimal FastAPI application."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_frontend() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "APRENDIZ" in response.text
    assert 'class="language-switch"' in response.text
    assert 'id="processing-console"' in response.text


def test_project_status() -> None:
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json() == {"project": "APRENDIZ", "status": "mvp_in_progress"}


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
