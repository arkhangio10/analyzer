"""Tests for backend-driven visible processing sessions."""

import pytest

from app.models.processing import RobotMotionProcessingRequest
from app.services.processing_service import (
    ProcessingSessionNotFoundError,
    RobotMotionProcessingService,
)


def request_payload() -> RobotMotionProcessingRequest:
    return RobotMotionProcessingRequest(
        task_name="Move a fragile component",
        objective="Learn a safe simulated pick-and-place procedure.",
        source="ui-reference://robot-demo",
        language="en",
        simulation_only=True,
    )


def test_processing_session_advances_and_exposes_real_results() -> None:
    now = [100.0]
    service = RobotMotionProcessingService(
        clock=lambda: now[0],
        stage_duration_seconds=1,
    )

    created = service.start(request_payload())

    assert created.status == "processing"
    assert created.progress_percent == 0
    assert created.current_stage_index == 0
    assert created.cloud_calls_made == 0
    assert created.training_result is None

    now[0] = 102.2
    processing = service.get(created.session_id)
    assert processing.completed_stage_count == 2
    assert processing.current_stage_index == 2
    assert processing.progress_percent == 44

    now[0] = 105.0
    completed = service.get(created.session_id)
    assert completed.status == "completed"
    assert completed.progress_percent == 100
    assert completed.current_stage_index is None
    assert completed.training_result is not None
    assert completed.training_result.safety_passed is True
    assert completed.training_result.metrics is not None
    assert completed.training_result.metrics.joint_count == 6
    assert completed.evaluation_result is not None
    assert completed.evaluation_result.passed is True
    assert completed.evaluation_result.score == 1


def test_unknown_processing_session_is_visible() -> None:
    service = RobotMotionProcessingService()

    with pytest.raises(ProcessingSessionNotFoundError):
        service.get("missing")


def test_invalid_processing_duration_is_rejected() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        RobotMotionProcessingService(stage_duration_seconds=0)

