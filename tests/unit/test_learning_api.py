"""Tests for reconciliation and protected evaluation."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _procedure(action: str, rule: str = "Keep a safe distance.") -> dict:
    return {
        "task": "Run like a dog",
        "objective": "Produce a stable quadruped running gait.",
        "inputs": ["lateral running reference"],
        "outputs": ["simulated gait"],
        "steps": [
            {
                "step": 1,
                "action": action,
                "expected_result": "Stable acceleration",
            }
        ],
        "rules": [rule],
        "conditions": ["Simulation only"],
        "exceptions": ["Stop after a fall"],
    }


def test_reconciliation_marks_full_agreement_ready_for_practice() -> None:
    response = client.post(
        "/api/learning/reconcile",
        json={
            "task": "Run like a dog",
            "sources": [
                {"source_id": "video-a", "approved": True, "procedure": _procedure("Accelerate with a diagonal gait.")},
                {"source_id": "video-b", "approved": True, "procedure": _procedure("Accelerate with a diagonal gait")},
            ],
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["ready_for_practice"] is True
    assert result["confidence"] == 1.0
    assert result["conflicts"] == []
    assert "2/2 approved sources" in result["procedure"]["steps"][0]["evidence"]


def test_reconciliation_exposes_conflicting_actions() -> None:
    response = client.post(
        "/api/learning/reconcile",
        json={
            "task": "Run like a dog",
            "sources": [
                {"source_id": "video-a", "approved": True, "procedure": _procedure("Use a diagonal gait")},
                {"source_id": "video-b", "approved": True, "procedure": _procedure("Use a bounding gait")},
            ],
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["ready_for_practice"] is False
    assert len(result["conflicts"]) == 1


def test_frozen_evaluation_passes_without_disclosing_expected_values() -> None:
    response = client.post(
        "/api/learning/evaluate/frozen",
        json={
            "evaluation_id": "eval-001",
            "skill_id": "dog-gait-v1",
            "case_id": "robot-gait-sim-001",
            "actual_output": {
                "simulation_only": True,
                "safety_passed": True,
                "falls": 0,
                "joint_limit_violations": 0,
            },
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["passed"] is True
    assert result["score"] == 1.0
    assert result["expected_output_disclosed"] is False
    assert "expected_output" not in result


def test_frozen_evaluation_reports_field_failure_without_answer() -> None:
    response = client.post(
        "/api/learning/evaluate/frozen",
        json={
            "evaluation_id": "eval-002",
            "skill_id": "dog-gait-v1",
            "case_id": "robot-gait-sim-001",
            "actual_output": {
                "simulation_only": True,
                "safety_passed": False,
                "falls": 1,
                "joint_limit_violations": 0,
            },
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["passed"] is False
    assert result["score"] == 0.5
    assert all("expected result" in failure for failure in result["failures"])


def test_unknown_frozen_case_returns_not_found() -> None:
    response = client.post(
        "/api/learning/evaluate/frozen",
        json={
            "evaluation_id": "eval-003",
            "skill_id": "missing",
            "case_id": "missing",
            "actual_output": {},
        },
    )
    assert response.status_code == 404
