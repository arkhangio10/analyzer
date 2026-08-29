"""Smoke tests for the minimal FastAPI application."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_project_status() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"project": "APRENDIZ", "status": "initializing"}


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
