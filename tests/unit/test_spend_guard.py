"""Tests for the guard on endpoints that can spend the operator's money.

The service is deployed public and unauthenticated, because the QC console is
what other people need and it costs nothing to serve. The endpoints that reach
a provider are the exception, and this file holds three properties:

- reading stays open, so nothing the console needs is behind a token;
- a configured token is actually required, and a wrong one is rejected;
- **every** POST route is either guarded or on a short list of free ones with a
  stated reason. That last test is the one that matters over time: adding a new
  endpoint that spends money fails here until somebody decides which it is,
  rather than shipping unguarded because a decorator was forgotten.
"""

from __future__ import annotations

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.spend_guard import (
    SPEND_TOKEN_HEADER,
    require_spend_authorization,
    spend_endpoints_are_protected,
    spend_token_is_required,
)
from app.core.config import Settings
from app.main import app


client = TestClient(app)


# Routes that accept a POST and cannot reach a provider. Each is here because
# it is deterministic or purely local, not because guarding it was awkward.
FREE_POST_ROUTES = {
    "/api/projects": "Creates a project record; contacts nothing.",
    "/api/projects/{project_id}/uploads": "Writes a file the user supplied.",
    "/api/projects/{project_id}/video-procedures/{extraction_id}/review":
        "The human approval gate itself. Free, and gating it would be circular.",
    "/api/projects/{project_id}/video-procedures/{extraction_id}/adapt":
        "Deterministic destination adaptation over an existing record.",
    "/api/projects/{project_id}/computer-practices": "Drafts a local rehearsal.",
    "/api/projects/{project_id}/computer-practices/{practice_id}/execute":
        "Runs an approved browser action in the container; no provider.",
    "/api/qc/projects/{project_id}/extractions/{extraction_id}/prove":
        "Recomputes a verdict from stored samples; the pipeline calls no model.",
    "/api/sources/search/{search_id}/approve":
        "Records which candidates a person approved; contacts nothing.",
    "/api/execution/computer/execute": "Managed local file actions.",
    "/api/execution/computer/validate": "Deterministic validation.",
    "/api/execution/computer/browser/execute": "Allowlisted browser action.",
    "/api/learning/evaluate/frozen": "Runs the frozen evaluation set locally.",
    "/api/learning/reconcile": "Deterministic comparison of stored procedures.",
    "/api/processing/robot-motion": "Local simulation; reports zero cloud calls.",
    "/api/robots/profiles/arp-1/import/urdf": "Parses a URDF; contacts nothing.",
    "/api/robots/profiles/arp-1/motion-contract": "Deterministic contract build.",
    "/api/training/robot-motion": "Stores an instructor demonstration.",
    "/api/training/robot-motion/{session_id}/evaluate": "Local replay evaluation.",
}


def api_routes(routes=None):
    """Yield every APIRoute, descending into included routers.

    This FastAPI keeps an included router as an `_IncludedRouter` wrapper
    rather than flattening its routes into `app.routes`, so a walk that only
    checks `isinstance(route, APIRoute)` at the top level finds nothing at all
    -- and every test built on it then passes while checking nothing. That is
    exactly what the first version of this file did. Hence the recursion, and
    hence `test_the_walk_finds_routes_at_all` below.
    """
    for route in app.routes if routes is None else routes:
        if isinstance(route, APIRoute):
            yield route
            continue
        inner = getattr(route, "original_router", None)
        if inner is not None:
            yield from api_routes(inner.routes)
        else:
            yield from api_routes(getattr(route, "routes", []) or [])


def post_routes():
    return [route for route in api_routes() if "POST" in route.methods]


def guarded_paths() -> set[str]:
    """Return the paths whose POST requires the spend token."""
    return {
        route.path
        for route in post_routes()
        for dependency in route.dependencies
        if dependency.dependency is require_spend_authorization
    }


def all_post_paths() -> set[str]:
    return {route.path for route in post_routes()}


def test_the_walk_finds_routes_at_all() -> None:
    """Guards every other test here: an empty walk would pass them vacuously."""
    assert len(all_post_paths()) > 15, all_post_paths()


# --- the structural property ----------------------------------------------


def test_every_post_route_is_guarded_or_listed_as_free() -> None:
    """A new endpoint that spends must not ship because a decorator was missed."""
    unaccounted = all_post_paths() - guarded_paths() - set(FREE_POST_ROUTES)

    assert not unaccounted, (
        "These POST routes neither require the spend token nor appear in "
        f"FREE_POST_ROUTES: {sorted(unaccounted)}. If one can reach a "
        "provider, add Depends(require_spend_authorization). If it cannot, "
        "list it with the reason."
    )


def test_the_known_paid_endpoints_are_guarded() -> None:
    guarded = guarded_paths()

    for path in (
        "/api/experiments/video/extract",
        "/api/projects/{project_id}/video-procedures/extract",
        "/api/projects/{project_id}/video-procedures/{extraction_id}/motion-analysis",
        "/api/sources/search",
    ):
        assert path in guarded, path


def test_nothing_free_was_guarded_by_accident() -> None:
    """Guarding a free endpoint would put the console behind a token."""
    assert guarded_paths().isdisjoint(FREE_POST_ROUTES)


# --- what the console needs stays open ------------------------------------


def test_reading_the_console_never_needs_a_token() -> None:
    assert client.get("/qc").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/api/status").status_code == 200


def test_status_reports_whether_spending_is_protected() -> None:
    body = client.get("/api/status").json()

    assert "spend_endpoints_protected" in body
    assert isinstance(body["spend_endpoints_protected"], bool)


# --- when the guard is inert, and when it is not --------------------------


def test_an_endpoint_that_cannot_spend_needs_no_token() -> None:
    """Locally, provider calls are off, so requiring a token would be theatre."""
    assert spend_endpoints_are_protected(Settings(google_genai_enabled=False)) is True


def test_enabling_provider_calls_without_a_token_is_reported_unprotected() -> None:
    settings = Settings(google_genai_enabled=True, spend_token=None)

    assert spend_endpoints_are_protected(settings) is False


def test_a_token_protects_an_enabled_deployment() -> None:
    settings = Settings(google_genai_enabled=True, spend_token="s3cret")

    assert spend_endpoints_are_protected(settings) is True


# --- the guard itself ------------------------------------------------------


@pytest.fixture
def configured(monkeypatch):
    """Run the app as a deployment with provider calls enabled and a token."""
    from app.api import spend_guard

    monkeypatch.setattr(
        spend_guard,
        "get_settings",
        lambda: Settings(google_genai_enabled=True, spend_token="s3cret"),
    )
    return "s3cret"


def test_a_paid_endpoint_refuses_without_the_header(configured) -> None:
    response = client.post(
        "/api/sources/search", json={"query": "walking", "max_results": 3}
    )

    assert response.status_code == 401
    assert SPEND_TOKEN_HEADER in response.json()["detail"]


def test_a_paid_endpoint_refuses_a_wrong_token(configured) -> None:
    response = client.post(
        "/api/sources/search",
        json={"query": "walking", "max_results": 3},
        headers={SPEND_TOKEN_HEADER: "not-the-token"},
    )

    assert response.status_code == 401


def test_the_right_token_gets_past_the_guard(configured) -> None:
    """Past the guard, not necessarily to a result: YouTube may be unconfigured."""
    response = client.post(
        "/api/sources/search",
        json={"query": "walking", "max_results": 3},
        headers={SPEND_TOKEN_HEADER: configured},
    )

    assert response.status_code != 401


def test_an_enabled_deployment_without_a_token_refuses_to_serve(monkeypatch) -> None:
    """The dangerous state is an oversight far more often than a decision."""
    from app.api import spend_guard

    monkeypatch.setattr(
        spend_guard,
        "get_settings",
        lambda: Settings(google_genai_enabled=True, spend_token=None),
    )

    response = client.post(
        "/api/sources/search", json={"query": "walking", "max_results": 3}
    )

    assert response.status_code == 503
    assert "no spend token is configured" in response.json()["detail"]


# --- telling the console a token is expected -------------------------------
#
# Without this the console can only learn the requirement by spending a
# request on a 401, and the person then has nowhere to put the token.


def test_no_token_configured_is_not_required() -> None:
    assert spend_token_is_required(Settings(spend_token=None)) is False


def test_a_configured_token_is_reported_required() -> None:
    """Reported whether or not provider calls are on: the guard checks either way."""
    assert spend_token_is_required(Settings(spend_token="s3cret")) is True
    assert (
        spend_token_is_required(
            Settings(google_genai_enabled=True, spend_token="s3cret")
        )
        is True
    )


def test_status_reports_the_requirement_without_revealing_the_token(
    configured,
) -> None:
    """The console reads this to decide whether to ask for a token."""
    response = client.get("/api/status")

    assert response.json()["spend_token_required"] is True
    assert configured not in response.text


def test_status_reports_no_requirement_when_no_token_is_configured() -> None:
    assert client.get("/api/status").json()["spend_token_required"] is False
