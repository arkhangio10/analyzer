"""Schematic preview data for the visible robot-motion animation.

The interface animates a demonstration so a person can see what was learned
before approving anything. This module only assigns each joint a drawing role
and forwards the already validated waypoints. It does not solve kinematics,
simulate dynamics, check collisions, or describe hardware behavior.
"""

from __future__ import annotations

from app.models.robot_motion import (
    MotionPreviewJoint,
    MotionPreviewRole,
    MotionWaypoint,
    RobotMotionPreview,
)


SIMARM6_MODEL = "APRENDIZ SimArm-6"

_SIMARM6_LAYOUT: tuple[tuple[int, str, MotionPreviewRole, float], ...] = (
    (0, "base yaw", MotionPreviewRole.BASE_YAW, 0.0),
    (1, "shoulder pitch", MotionPreviewRole.PLANAR_LINK, 0.42),
    (2, "elbow pitch", MotionPreviewRole.PLANAR_LINK, 0.28),
    (3, "forearm roll", MotionPreviewRole.ROLL, 0.0),
    (4, "wrist pitch", MotionPreviewRole.PLANAR_LINK, 0.16),
    (5, "wrist roll", MotionPreviewRole.ROLL, 0.0),
)

_MAX_PLANAR_LINKS = 4


def _simarm6_joints() -> list[MotionPreviewJoint]:
    return [
        MotionPreviewJoint(
            joint_index=index,
            label=label,
            role=role,
            length_ratio=length_ratio,
        )
        for index, label, role, length_ratio in _SIMARM6_LAYOUT
    ]


def _generic_joints(joint_count: int) -> list[MotionPreviewJoint]:
    """Describe an unknown chain without inventing a specific robot.

    The first joint is drawn as a base rotation, the next joints become a
    shortening planar chain, and any remaining joint is shown as a dial. The
    result is a readable diagram, not a claim about real link geometry.
    """
    joints: list[MotionPreviewJoint] = []
    planar_used = 0
    for index in range(joint_count):
        if index == 0 and joint_count > 1:
            role, length_ratio = MotionPreviewRole.BASE_YAW, 0.0
        elif planar_used < _MAX_PLANAR_LINKS:
            role = MotionPreviewRole.PLANAR_LINK
            length_ratio = round(0.34 - planar_used * 0.06, 2)
            planar_used += 1
        else:
            role, length_ratio = MotionPreviewRole.ROLL, 0.0
        joints.append(
            MotionPreviewJoint(
                joint_index=index,
                label=f"joint {index}",
                role=role,
                length_ratio=length_ratio,
            )
        )
    return joints


def build_motion_preview(
    *,
    robot_model: str,
    waypoints: list[MotionWaypoint],
) -> RobotMotionPreview:
    """Return schematic drawing data for one validated demonstration."""
    if len(waypoints) < 2:
        raise ValueError("A motion preview needs at least two waypoints")

    joint_count = len(waypoints[0].joint_positions_degrees)
    is_reference_arm = (
        robot_model == SIMARM6_MODEL and joint_count == len(_SIMARM6_LAYOUT)
    )
    joints = (
        _simarm6_joints() if is_reference_arm else _generic_joints(joint_count)
    )
    return RobotMotionPreview(
        robot_model=robot_model,
        duration_seconds=max(point.timestamp_seconds for point in waypoints),
        joints=joints,
        waypoints=list(waypoints),
    )
