"""Deterministic robot-motion procedure acquisition and evaluation."""

from __future__ import annotations

import math
from statistics import fmean
from uuid import uuid4

from app.models.evaluation import EvaluationResult
from app.models.procedure import Procedure, ProcedureStep
from app.models.robot_motion import (
    JointLimit,
    MotionWaypoint,
    RobotMotionEvaluationRequest,
    RobotMotionMetrics,
    RobotMotionTrainingRequest,
    RobotMotionTrainingResult,
    RobotMotionSessionRecord,
    RobotMotionTrainingStatus,
)
from app.services.record_store import JsonRecordStore


class RobotMotionSessionNotFoundError(LookupError):
    """Raised when an evaluation references an unknown training session."""


class RobotMotionSessionRejectedError(ValueError):
    """Raised when evaluation is requested for an unsafe demonstration."""


class RobotMotionTrainingService:
    """Acquire procedural memory from structured motion demonstrations.

    This service never sends commands to hardware. It validates instructor
    data, derives inspectable procedural steps, and evaluates candidate replay
    data against the stored external reference.
    """

    def __init__(self, store: JsonRecordStore | None = None) -> None:
        self._store = store
        records = store.load_all(RobotMotionSessionRecord) if store else {}
        self._records: dict[str, RobotMotionSessionRecord] = records
        self._requests = {
            session_id: record.request for session_id, record in records.items()
        }
        self._results = {
            session_id: record.result for session_id, record in records.items()
        }

    @property
    def is_durable(self) -> bool:
        """Report whether sessions and evaluations survive a restart."""
        return bool(self._store and self._store.is_durable)

    def _retain(self, record: RobotMotionSessionRecord) -> None:
        session_id = record.result.session_id
        self._records[session_id] = record
        self._requests[session_id] = record.request
        self._results[session_id] = record.result
        if self._store:
            self._store.save(session_id, record)

    def train(self, request: RobotMotionTrainingRequest) -> RobotMotionTrainingResult:
        """Validate one demonstration and convert it into a procedure."""
        session_id = f"robot-motion-{uuid4()}"
        violations, warnings = self._validate_demonstration(
            request.waypoints,
            request.joint_limits,
        )
        if not request.instructor_verified:
            warnings.append(
                "The demonstration is not marked as instructor-verified; "
                "the extracted procedure remains observation-only."
            )

        if violations:
            result = RobotMotionTrainingResult(
                session_id=session_id,
                status=RobotMotionTrainingStatus.REJECTED,
                safety_passed=False,
                safety_violations=violations,
                warnings=warnings,
                validation_scope="not_validated",
            )
        else:
            metrics = self._measure(request.waypoints)
            procedure = self._build_procedure(request)
            result = RobotMotionTrainingResult(
                session_id=session_id,
                status=RobotMotionTrainingStatus.PROCEDURE_EXTRACTED,
                safety_passed=True,
                warnings=warnings,
                metrics=metrics,
                procedure=procedure,
                validation_scope=(
                    "instructor_demonstration"
                    if request.instructor_verified
                    else "not_validated"
                ),
            )

        self._retain(RobotMotionSessionRecord(request=request, result=result))
        return result

    def get_result(self, session_id: str) -> RobotMotionTrainingResult:
        """Return a previously processed training result."""
        try:
            return self._results[session_id]
        except KeyError as error:
            raise RobotMotionSessionNotFoundError(session_id) from error

    def evaluate(
        self,
        session_id: str,
        request: RobotMotionEvaluationRequest,
    ) -> EvaluationResult:
        """Compare candidate motion with its instructor-provided reference."""
        training_result = self.get_result(session_id)
        if training_result.status is RobotMotionTrainingStatus.REJECTED:
            raise RobotMotionSessionRejectedError(session_id)

        reference = self._requests[session_id]
        violations, _ = self._validate_demonstration(
            request.waypoints,
            reference.joint_limits,
        )
        failures = [f"Safety: {violation}" for violation in violations]

        if len(request.waypoints) != len(reference.waypoints):
            failures.append(
                "Waypoint count does not match the instructor demonstration: "
                f"expected {len(reference.waypoints)}, got {len(request.waypoints)}."
            )

        reference_joint_count = len(reference.waypoints[0].joint_positions_degrees)
        candidate_joint_count = len(request.waypoints[0].joint_positions_degrees)
        if candidate_joint_count != reference_joint_count:
            failures.append(
                "Joint count does not match the instructor demonstration: "
                f"expected {reference_joint_count}, got {candidate_joint_count}."
            )

        if failures:
            evaluation = EvaluationResult(
                evaluation_id=request.execution_id,
                skill_id=session_id,
                passed=False,
                actual_output={
                    "waypoint_count": len(request.waypoints),
                    "joint_count": candidate_joint_count,
                    "safety_passed": not violations,
                },
                expected_output={
                    "waypoint_count": len(reference.waypoints),
                    "joint_count": reference_joint_count,
                    "source": reference.source,
                },
                score=0,
                failures=failures,
                notes=self._evaluation_note(),
            )
            self._retain_evaluation(session_id, evaluation)
            return evaluation

        joint_errors = [
            abs(actual - expected)
            for expected_waypoint, actual_waypoint in zip(
                reference.waypoints,
                request.waypoints,
                strict=True,
            )
            for expected, actual in zip(
                expected_waypoint.joint_positions_degrees,
                actual_waypoint.joint_positions_degrees,
                strict=True,
            )
        ]
        mean_joint_error = fmean(joint_errors)
        maximum_joint_error = max(joint_errors)
        expected_duration = self._duration(reference.waypoints)
        actual_duration = self._duration(request.waypoints)
        duration_error = abs(actual_duration - expected_duration)

        if maximum_joint_error > request.joint_tolerance_degrees:
            failures.append(
                "Maximum joint error exceeds tolerance: "
                f"{maximum_joint_error:.3f}° > "
                f"{request.joint_tolerance_degrees:.3f}°."
            )
        if duration_error > request.duration_tolerance_seconds:
            failures.append(
                "Duration error exceeds tolerance: "
                f"{duration_error:.3f}s > "
                f"{request.duration_tolerance_seconds:.3f}s."
            )

        position_score = max(
            0.0,
            1.0 - mean_joint_error / (2 * request.joint_tolerance_degrees),
        )
        if request.duration_tolerance_seconds == 0:
            duration_score = 1.0 if duration_error == 0 else 0.0
        else:
            duration_score = max(
                0.0,
                1.0 - duration_error / (2 * request.duration_tolerance_seconds),
            )
        score = round(position_score * 0.85 + duration_score * 0.15, 6)

        evaluation = EvaluationResult(
            evaluation_id=request.execution_id,
            skill_id=session_id,
            passed=not failures,
            actual_output={
                "mean_joint_error_degrees": round(mean_joint_error, 6),
                "maximum_joint_error_degrees": round(maximum_joint_error, 6),
                "duration_seconds": round(actual_duration, 6),
                "duration_error_seconds": round(duration_error, 6),
                "safety_passed": True,
            },
            expected_output={
                "maximum_joint_error_degrees": request.joint_tolerance_degrees,
                "duration_seconds": round(expected_duration, 6),
                "duration_tolerance_seconds": request.duration_tolerance_seconds,
                "source": reference.source,
            },
            score=score,
            failures=failures,
            notes=self._evaluation_note(),
        )
        self._retain_evaluation(session_id, evaluation)
        return evaluation

    def _retain_evaluation(
        self,
        session_id: str,
        evaluation: EvaluationResult,
    ) -> None:
        record = self._records[session_id]
        evaluations = [*record.evaluations, evaluation][-100:]
        self._retain(record.model_copy(update={"evaluations": evaluations}))

    @staticmethod
    def _validate_demonstration(
        waypoints: list[MotionWaypoint],
        limits: list[JointLimit],
    ) -> tuple[list[str], list[str]]:
        violations: list[str] = []
        warnings: list[str] = []
        joint_count = len(waypoints[0].joint_positions_degrees)
        limit_by_joint: dict[int, JointLimit] = {}

        for limit in limits:
            if limit.joint_index in limit_by_joint:
                violations.append(
                    f"Joint {limit.joint_index} has more than one safety limit."
                )
            limit_by_joint[limit.joint_index] = limit
            if not all(
                math.isfinite(value)
                for value in (
                    limit.minimum_degrees,
                    limit.maximum_degrees,
                    limit.maximum_velocity_degrees_per_second,
                )
            ):
                violations.append(
                    f"Joint {limit.joint_index} contains a non-finite safety limit."
                )
            if limit.minimum_degrees >= limit.maximum_degrees:
                violations.append(
                    f"Joint {limit.joint_index} minimum must be below maximum."
                )

        expected_indices = set(range(joint_count))
        if set(limit_by_joint) != expected_indices:
            violations.append(
                "Joint limits must cover every demonstrated joint exactly once: "
                f"expected {sorted(expected_indices)}, got {sorted(limit_by_joint)}."
            )

        for waypoint_index, waypoint in enumerate(waypoints):
            if len(waypoint.joint_positions_degrees) != joint_count:
                violations.append(
                    f"Waypoint {waypoint_index} has an inconsistent joint count."
                )
                continue
            if not math.isfinite(waypoint.timestamp_seconds):
                violations.append(
                    f"Waypoint {waypoint_index} timestamp is not finite."
                )
            for joint_index, position in enumerate(
                waypoint.joint_positions_degrees
            ):
                if not math.isfinite(position):
                    violations.append(
                        f"Waypoint {waypoint_index}, joint {joint_index} "
                        "position is not finite."
                    )
                    continue
                limit = limit_by_joint.get(joint_index)
                if limit and not (
                    limit.minimum_degrees <= position <= limit.maximum_degrees
                ):
                    violations.append(
                        f"Waypoint {waypoint_index}, joint {joint_index} is outside "
                        f"its safe range: {position}° not in "
                        f"[{limit.minimum_degrees}°, {limit.maximum_degrees}°]."
                    )

            if waypoint_index == 0:
                continue
            previous = waypoints[waypoint_index - 1]
            delta_time = waypoint.timestamp_seconds - previous.timestamp_seconds
            if delta_time <= 0:
                violations.append(
                    f"Waypoint {waypoint_index} timestamp must be strictly increasing."
                )
                continue
            if len(previous.joint_positions_degrees) != joint_count:
                continue
            for joint_index, (start, end) in enumerate(
                zip(
                    previous.joint_positions_degrees,
                    waypoint.joint_positions_degrees,
                    strict=True,
                )
            ):
                limit = limit_by_joint.get(joint_index)
                if limit is None:
                    continue
                velocity = abs(end - start) / delta_time
                if velocity > limit.maximum_velocity_degrees_per_second:
                    violations.append(
                        f"Segment {waypoint_index - 1}->{waypoint_index}, joint "
                        f"{joint_index} exceeds maximum velocity: {velocity:.3f}°/s "
                        f"> {limit.maximum_velocity_degrees_per_second:.3f}°/s."
                    )

        if waypoints[0].timestamp_seconds != 0:
            warnings.append(
                "The first waypoint does not start at 0 seconds; durations are "
                "normalized from the first timestamp."
            )
        return list(dict.fromkeys(violations)), warnings

    @staticmethod
    def _measure(waypoints: list[MotionWaypoint]) -> RobotMotionMetrics:
        path_length = 0.0
        peak_velocity = 0.0
        for previous, current in zip(waypoints, waypoints[1:]):
            deltas = [
                end - start
                for start, end in zip(
                    previous.joint_positions_degrees,
                    current.joint_positions_degrees,
                    strict=True,
                )
            ]
            path_length += math.sqrt(sum(delta * delta for delta in deltas))
            delta_time = current.timestamp_seconds - previous.timestamp_seconds
            peak_velocity = max(
                peak_velocity,
                *(abs(delta) / delta_time for delta in deltas),
            )
        return RobotMotionMetrics(
            duration_seconds=round(
                RobotMotionTrainingService._duration(waypoints),
                6,
            ),
            path_length_degrees=round(path_length, 6),
            peak_velocity_degrees_per_second=round(peak_velocity, 6),
            waypoint_count=len(waypoints),
            joint_count=len(waypoints[0].joint_positions_degrees),
        )

    @staticmethod
    def _duration(waypoints: list[MotionWaypoint]) -> float:
        return waypoints[-1].timestamp_seconds - waypoints[0].timestamp_seconds

    @staticmethod
    def _build_procedure(request: RobotMotionTrainingRequest) -> Procedure:
        steps: list[ProcedureStep] = []
        for index, waypoint in enumerate(request.waypoints[1:], start=1):
            target = ", ".join(
                f"J{joint_index}={position:.3f}°"
                for joint_index, position in enumerate(
                    waypoint.joint_positions_degrees
                )
            )
            label = waypoint.label or f"waypoint {index}"
            gripper = (
                ""
                if waypoint.gripper_percent is None
                else f" Set gripper to {waypoint.gripper_percent:.1f}%."
            )
            steps.append(
                ProcedureStep(
                    step=index,
                    action=f"Move {request.robot_model} to {label}.",
                    condition=(
                        "Run in simulation and enforce every declared joint and "
                        "velocity limit."
                    ),
                    expected_result=(
                        f"Reach [{target}] at t={waypoint.timestamp_seconds:.3f}s."
                        f"{gripper}"
                    ),
                )
            )

        rules = [
            (
                f"Joint {limit.joint_index}: remain between "
                f"{limit.minimum_degrees}° and {limit.maximum_degrees}° and below "
                f"{limit.maximum_velocity_degrees_per_second}°/s."
            )
            for limit in sorted(request.joint_limits, key=lambda item: item.joint_index)
        ]
        rules.insert(0, "Simulation only; this procedure cannot command hardware.")
        return Procedure(
            task=request.task_name,
            objective=request.objective,
            inputs=[
                "ordered joint-position waypoints",
                "monotonic timestamps in seconds",
                "joint safety limits",
                "optional gripper percentage",
            ],
            outputs=[
                "inspectable motion procedure",
                "deterministic motion metrics",
                "safety validation evidence",
            ],
            steps=steps,
            rules=rules,
            conditions=[
                f"Robot model: {request.robot_model}",
                "A human instructor must approve the procedure before hardware use.",
            ],
            exceptions=[
                "Reject non-monotonic timestamps.",
                "Reject joint positions or velocities outside declared limits.",
                "Stop evaluation when waypoint or joint topology differs.",
            ],
            examples=[
                f"Instructor demonstration {request.demonstration_id} from "
                f"{request.source}."
            ],
        )

    @staticmethod
    def _evaluation_note() -> str:
        return (
            "Instructor-grounded replay evaluation. It measures imitation only; "
            "it does not validate generalization, collision avoidance, dynamics, "
            "or physical hardware safety."
        )
