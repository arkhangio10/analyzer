"""Backend-driven progress for the local robot-motion vertical slice."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic
from uuid import uuid4

from app.models.evaluation import EvaluationResult
from app.models.processing import (
    ProcessingStatus,
    RobotMotionProcessingRequest,
    RobotMotionProcessingSession,
)
from app.models.robot_motion import (
    JointLimit,
    MotionWaypoint,
    RobotMotionEvaluationRequest,
    RobotMotionTrainingRequest,
    RobotMotionTrainingResult,
)
from app.services.robot_motion_training import RobotMotionTrainingService


class ProcessingSessionNotFoundError(LookupError):
    """Raised when a visible processing session does not exist."""


@dataclass(frozen=True)
class _ProcessingRecord:
    started_at: float
    training_result: RobotMotionTrainingResult
    evaluation_result: EvaluationResult


class RobotMotionProcessingService:
    """Expose deterministic local work as a pollable processing session.

    The current slice processes a built-in, simulation-only joint trajectory.
    It does not inspect the supplied video reference and never calls a cloud
    model. The provider boundary can replace this local source in a later
    milestone without changing the session contract used by the frontend.
    """

    _STAGE_COUNT = 5

    def __init__(
        self,
        *,
        clock: Callable[[], float] = monotonic,
        stage_duration_seconds: float = 0.8,
    ) -> None:
        if stage_duration_seconds <= 0:
            raise ValueError("stage_duration_seconds must be positive")
        self._clock = clock
        self._stage_duration_seconds = stage_duration_seconds
        self._records: dict[str, _ProcessingRecord] = {}
        self._training_service = RobotMotionTrainingService()

    def start(
        self,
        request: RobotMotionProcessingRequest,
    ) -> RobotMotionProcessingSession:
        """Create a processing session backed by validated local work."""
        processing_session_id = f"processing-{uuid4()}"
        demonstration = self._reference_demonstration(request)
        training_result = self._training_service.train(demonstration)
        evaluation_result = self._training_service.evaluate(
            training_result.session_id,
            RobotMotionEvaluationRequest(
                execution_id=f"replay-{uuid4()}",
                waypoints=demonstration.waypoints,
                joint_tolerance_degrees=2,
                duration_tolerance_seconds=0.25,
            ),
        )
        self._records[processing_session_id] = _ProcessingRecord(
            started_at=self._clock(),
            training_result=training_result,
            evaluation_result=evaluation_result,
        )
        return self.get(processing_session_id)

    def get(self, session_id: str) -> RobotMotionProcessingSession:
        """Return progress derived from monotonic elapsed time."""
        try:
            record = self._records[session_id]
        except KeyError as error:
            raise ProcessingSessionNotFoundError(session_id) from error

        elapsed = max(0.0, self._clock() - record.started_at)
        total_duration = self._stage_duration_seconds * self._STAGE_COUNT
        completed = min(
            self._STAGE_COUNT,
            int(elapsed / self._stage_duration_seconds),
        )
        is_complete = completed >= self._STAGE_COUNT
        progress = 100 if is_complete else min(
            99,
            int(elapsed / total_duration * 100),
        )

        return RobotMotionProcessingSession(
            session_id=session_id,
            status=(
                ProcessingStatus.COMPLETED
                if is_complete
                else ProcessingStatus.PROCESSING
            ),
            progress_percent=progress,
            current_stage_index=None if is_complete else completed,
            completed_stage_count=completed,
            training_result=record.training_result if is_complete else None,
            evaluation_result=record.evaluation_result if is_complete else None,
        )

    @staticmethod
    def _reference_demonstration(
        request: RobotMotionProcessingRequest,
    ) -> RobotMotionTrainingRequest:
        waypoints = [
            MotionWaypoint(
                timestamp_seconds=0,
                joint_positions_degrees=[0, -20, 35, 0, 45, 0],
                gripper_percent=100,
                label="home",
            ),
            MotionWaypoint(
                timestamp_seconds=1,
                joint_positions_degrees=[10, -25, 40, 0, 40, 5],
                gripper_percent=100,
                label="approach object",
            ),
            MotionWaypoint(
                timestamp_seconds=2,
                joint_positions_degrees=[15, -35, 50, 0, 35, 5],
                gripper_percent=100,
                label="pre-grasp",
            ),
            MotionWaypoint(
                timestamp_seconds=3,
                joint_positions_degrees=[15, -35, 50, 0, 35, 5],
                gripper_percent=30,
                label="grasp",
            ),
            MotionWaypoint(
                timestamp_seconds=4.5,
                joint_positions_degrees=[0, -20, 35, 10, 45, 0],
                gripper_percent=30,
                label="lift",
            ),
            MotionWaypoint(
                timestamp_seconds=6,
                joint_positions_degrees=[-20, -15, 30, 15, 50, -10],
                gripper_percent=30,
                label="clear obstacles",
            ),
            MotionWaypoint(
                timestamp_seconds=7.5,
                joint_positions_degrees=[-35, -30, 45, 10, 40, -5],
                gripper_percent=30,
                label="approach container",
            ),
            MotionWaypoint(
                timestamp_seconds=8.5,
                joint_positions_degrees=[-35, -35, 50, 10, 35, -5],
                gripper_percent=30,
                label="place vertically",
            ),
            MotionWaypoint(
                timestamp_seconds=9.5,
                joint_positions_degrees=[-35, -35, 50, 10, 35, -5],
                gripper_percent=100,
                label="release",
            ),
            MotionWaypoint(
                timestamp_seconds=11,
                joint_positions_degrees=[0, -20, 35, 0, 45, 0],
                gripper_percent=100,
                label="return home",
            ),
        ]
        joint_limits = [
            JointLimit(
                joint_index=index,
                minimum_degrees=-180,
                maximum_degrees=180,
                maximum_velocity_degrees_per_second=60,
            )
            for index in range(6)
        ]
        return RobotMotionTrainingRequest(
            task_name=request.task_name,
            objective=request.objective,
            robot_model="APRENDIZ SimArm-6",
            demonstration_id=f"guided-{uuid4()}",
            source=(
                "Built-in local simulation. User-provided reference retained "
                f"as metadata only: {request.source}"
            ),
            waypoints=waypoints,
            joint_limits=joint_limits,
            instructor_verified=False,
            simulation_only=True,
        )

