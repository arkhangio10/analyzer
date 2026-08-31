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
    assert 'name="destination" value="robot"' in response.text
    assert 'name="destination" value="computer"' in response.text
    assert 'name="source-type" value="automatic"' in response.text
    assert 'id="source-candidates"' in response.text
    assert 'id="computer-practice-panel"' in response.text
    assert 'id="browser-plan-preview"' in response.text
    assert 'id="browser-practice-approval"' in response.text
    assert 'id="video-procedure-panel"' in response.text
    assert 'id="video-cost-approval"' in response.text
    assert 'id="procedure-review"' in response.text
    assert 'role="dialog"' in response.text
    assert 'data-workspace-target="setup"' in response.text
    assert 'id="workspace-close"' in response.text
    assert 'id="procedure-step-pager"' in response.text
    assert 'id="motion-canvas"' in response.text
    assert 'id="motion-play"' in response.text
    assert 'id="motion-scrubber"' in response.text
    assert 'id="motion-ticks"' in response.text
    assert 'id="use-example"' in response.text
    assert 'data-step-jump="2"' in response.text
    assert 'id="extraction-activity"' in response.text
    assert 'id="extraction-elapsed"' in response.text
    assert 'id="video-next-step"' in response.text
    assert 'id="video-next-step-action"' in response.text
    assert 'id="recent-work"' in response.text
    assert 'id="recent-work-list"' in response.text
    assert 'rel="icon"' in response.text


def test_project_status() -> None:
    response = client.get("/api/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["project"] == "APRENDIZ"
    assert payload["status"] == "mvp_in_progress"
    assert isinstance(payload["durable_storage"], bool)
    assert payload["workflow_evidence_durable"] is True


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
