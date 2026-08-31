"""Tests for the schematic motion-preview contract used by the interface."""

import pytest

from app.models.robot_motion import MotionPreviewRole, MotionWaypoint
from app.services.motion_preview import SIMARM6_MODEL, build_motion_preview


def waypoints(joint_count: int = 6) -> list[MotionWaypoint]:
    return [
        MotionWaypoint(
            timestamp_seconds=0,
            joint_positions_degrees=[0.0] * joint_count,
            gripper_percent=100,
            label="home",
        ),
        MotionWaypoint(
            timestamp_seconds=2.5,
            joint_positions_degrees=[5.0] * joint_count,
            gripper_percent=30,
            label="grasp",
        ),
    ]


def test_reference_arm_gets_a_named_planar_chain() -> None:
    preview = build_motion_preview(
        robot_model=SIMARM6_MODEL,
        waypoints=waypoints(),
    )

    assert preview.preview_kind == "schematic_planar_projection"
    assert preview.physics_simulated is False
    assert preview.collision_checked is False
    assert preview.duration_seconds == 2.5
    assert [joint.role for joint in preview.joints] == [
        MotionPreviewRole.BASE_YAW,
        MotionPreviewRole.PLANAR_LINK,
        MotionPreviewRole.PLANAR_LINK,
        MotionPreviewRole.ROLL,
        MotionPreviewRole.PLANAR_LINK,
        MotionPreviewRole.ROLL,
    ]
    assert [joint.joint_index for joint in preview.joints] == [0, 1, 2, 3, 4, 5]
    planar_links = [
        joint
        for joint in preview.joints
        if joint.role is MotionPreviewRole.PLANAR_LINK
    ]
    assert all(joint.length_ratio > 0 for joint in planar_links)
    assert sum(joint.length_ratio for joint in preview.joints) <= 1


def test_waypoints_are_forwarded_unchanged() -> None:
    demonstration = waypoints()

    preview = build_motion_preview(
        robot_model=SIMARM6_MODEL,
        waypoints=demonstration,
    )

    assert preview.waypoints == demonstration


def test_unknown_robot_falls_back_to_a_generic_chain() -> None:
    preview = build_motion_preview(
        robot_model="Unlisted Arm",
        waypoints=waypoints(joint_count=3),
    )

    assert [joint.role for joint in preview.joints] == [
        MotionPreviewRole.BASE_YAW,
        MotionPreviewRole.PLANAR_LINK,
        MotionPreviewRole.PLANAR_LINK,
    ]
    assert all(joint.label for joint in preview.joints)


def test_matching_joint_count_alone_does_not_claim_the_reference_arm() -> None:
    preview = build_motion_preview(
        robot_model="Other Six Joint Arm",
        waypoints=waypoints(),
    )

    assert [joint.label for joint in preview.joints] == [
        f"joint {index}" for index in range(6)
    ]
    assert preview.joints[3].role is MotionPreviewRole.PLANAR_LINK


def test_single_waypoint_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least two waypoints"):
        build_motion_preview(
            robot_model=SIMARM6_MODEL,
            waypoints=waypoints()[:1],
        )
