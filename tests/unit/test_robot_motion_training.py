"""Tests for deterministic robot-motion procedural learning."""

import pytest

from app.models.robot_motion import (
    JointLimit,
    MotionWaypoint,
    RobotMotionEvaluationRequest,
    RobotMotionTrainingRequest,
    RobotMotionTrainingStatus,
)
from app.services.robot_motion_training import RobotMotionTrainingService


def training_request(
    *,
    waypoints: list[MotionWaypoint] | None = None,
    instructor_verified: bool = True,
) -> RobotMotionTrainingRequest:
    return RobotMotionTrainingRequest(
        task_name="Move a component between two trays",
        objective="Learn a safe pick-and-place joint trajectory.",
        robot_model="SimArm-2",
        demonstration_id="demo-pick-place-001",
        source="instructor://robotics-lab/session-001",
        waypoints=waypoints
        or [
            MotionWaypoint(
                timestamp_seconds=0,
                joint_positions_degrees=[0, 0],
                gripper_percent=100,
                label="home",
            ),
            MotionWaypoint(
                timestamp_seconds=1,
                joint_positions_degrees=[10, 5],
                gripper_percent=40,
                label="pick",
            ),
            MotionWaypoint(
                timestamp_seconds=2,
                joint_positions_degrees=[20, 10],
                gripper_percent=40,
                label="place",
            ),
        ],
        joint_limits=[
            JointLimit(
                joint_index=0,
                minimum_degrees=-90,
                maximum_degrees=90,
                maximum_velocity_degrees_per_second=20,
            ),
            JointLimit(
                joint_index=1,
                minimum_degrees=-45,
                maximum_degrees=45,
                maximum_velocity_degrees_per_second=10,
            ),
        ],
        instructor_verified=instructor_verified,
    )


def test_safe_demonstration_becomes_observation_procedure() -> None:
    service = RobotMotionTrainingService()

    result = service.train(training_request())

    assert result.status is RobotMotionTrainingStatus.PROCEDURE_EXTRACTED
    assert result.safety_passed is True
    assert result.validation_scope == "instructor_demonstration"
    assert result.procedure is not None
    assert len(result.procedure.steps) == 2
    assert result.procedure.steps[0].action == "Move SimArm-2 to pick."
    assert result.procedure.rules[0].startswith("Simulation only")
    assert result.metrics is not None
    assert result.metrics.duration_seconds == 2
    assert result.metrics.peak_velocity_degrees_per_second == 10
    assert result.metrics.path_length_degrees == pytest.approx(22.36068)


def test_unverified_demonstration_stays_explicitly_unvalidated() -> None:
    service = RobotMotionTrainingService()

    result = service.train(training_request(instructor_verified=False))

    assert result.status is RobotMotionTrainingStatus.PROCEDURE_EXTRACTED
    assert result.validation_scope == "not_validated"
    assert result.warnings


@pytest.mark.parametrize(
    "unsafe_waypoints, expected_fragment",
    [
        (
            [
                MotionWaypoint(
                    timestamp_seconds=0,
                    joint_positions_degrees=[0, 0],
                ),
                MotionWaypoint(
                    timestamp_seconds=1,
                    joint_positions_degrees=[100, 0],
                ),
            ],
            "outside its safe range",
        ),
        (
            [
                MotionWaypoint(
                    timestamp_seconds=0,
                    joint_positions_degrees=[0, 0],
                ),
                MotionWaypoint(
                    timestamp_seconds=0.1,
                    joint_positions_degrees=[10, 5],
                ),
            ],
            "exceeds maximum velocity",
        ),
    ],
)
def test_unsafe_demonstration_is_rejected(
    unsafe_waypoints: list[MotionWaypoint],
    expected_fragment: str,
) -> None:
    service = RobotMotionTrainingService()

    result = service.train(training_request(waypoints=unsafe_waypoints))

    assert result.status is RobotMotionTrainingStatus.REJECTED
    assert result.safety_passed is False
    assert result.procedure is None
    assert any(
        expected_fragment in violation
        for violation in result.safety_violations
    )


def test_candidate_replay_is_evaluated_against_instructor_reference() -> None:
    service = RobotMotionTrainingService()
    training = service.train(training_request())
    candidate = RobotMotionEvaluationRequest(
        execution_id="execution-001",
        waypoints=[
            MotionWaypoint(
                timestamp_seconds=0,
                joint_positions_degrees=[0.5, 0],
            ),
            MotionWaypoint(
                timestamp_seconds=1,
                joint_positions_degrees=[10.5, 5.5],
            ),
            MotionWaypoint(
                timestamp_seconds=2,
                joint_positions_degrees=[19.5, 10],
            ),
        ],
    )

    evaluation = service.evaluate(training.session_id, candidate)

    assert evaluation.passed is True
    assert evaluation.score is not None and evaluation.score > 0.9
    assert evaluation.actual_output["maximum_joint_error_degrees"] == 0.5
    assert evaluation.expected_output["source"].startswith("instructor://")


def test_candidate_replay_exposes_accuracy_failure() -> None:
    service = RobotMotionTrainingService()
    training = service.train(training_request())
    candidate = RobotMotionEvaluationRequest(
        execution_id="execution-002",
        waypoints=[
            MotionWaypoint(timestamp_seconds=0, joint_positions_degrees=[0, 0]),
            MotionWaypoint(timestamp_seconds=1, joint_positions_degrees=[16, 5]),
            MotionWaypoint(timestamp_seconds=2, joint_positions_degrees=[20, 10]),
        ],
    )

    evaluation = service.evaluate(training.session_id, candidate)

    assert evaluation.passed is False
    assert any("Maximum joint error" in failure for failure in evaluation.failures)


def test_non_monotonic_timestamps_are_rejected() -> None:
    service = RobotMotionTrainingService()
    result = service.train(
        training_request(
            waypoints=[
                MotionWaypoint(
                    timestamp_seconds=0,
                    joint_positions_degrees=[0, 0],
                ),
                MotionWaypoint(
                    timestamp_seconds=0,
                    joint_positions_degrees=[1, 1],
                ),
            ]
        )
    )

    assert result.status is RobotMotionTrainingStatus.REJECTED
    assert any(
        "timestamp must be strictly increasing" in violation
        for violation in result.safety_violations
    )
