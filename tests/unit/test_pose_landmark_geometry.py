"""Tests for the landmark-to-joint-angle arithmetic and its conventions.

The convention is the part worth testing: a straight knee is zero flexion, not
180 degrees, and every joint has its own neutral pose. Getting that wrong
produces angles that look plausible and mean nothing.
"""

from __future__ import annotations

from math import isclose

import pytest

from app.services.pose_landmark_geometry import (
    JOINT_DEFINITIONS,
    MEASURABLE_JOINTS,
    interior_angle,
    joint_flexion,
    landmark_name,
    required_landmarks,
)


# --- the raw angle ---------------------------------------------------------


def test_three_points_in_a_line_form_a_straight_angle() -> None:
    assert isclose(
        interior_angle((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.0, -1.0, 0.0)),
        180.0,
        abs_tol=1e-6,
    )


def test_perpendicular_limbs_form_a_right_angle() -> None:
    assert isclose(
        interior_angle((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
        90.0,
        abs_tol=1e-6,
    )


def test_a_folded_limb_closes_the_angle() -> None:
    assert isclose(
        interior_angle((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
        0.0,
        abs_tol=1e-6,
    )


def test_the_angle_is_three_dimensional() -> None:
    """Depth counts; a limb swinging toward the camera is not a straight limb."""
    assert isclose(
        interior_angle((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
        90.0,
        abs_tol=1e-6,
    )


def test_two_landmarks_at_the_same_place_have_no_angle() -> None:
    """A zero-length limb is a missing reading, not a zero-degree one."""
    assert interior_angle((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)) is None


def test_a_cosine_pushed_past_one_by_floating_point_still_answers() -> None:
    tiny = 1e-9
    angle = interior_angle((tiny, 0.0, 0.0), (0.0, 0.0, 0.0), (tiny * 2, 0.0, 0.0))
    assert angle is not None and isclose(angle, 0.0, abs_tol=1e-3)


# --- the flexion convention ------------------------------------------------


@pytest.mark.parametrize("joint_name", ["knee", "elbow", "hip"])
def test_a_straight_limb_is_zero_flexion(joint_name: str) -> None:
    """180 degrees of interior angle is a straight joint, which is neutral."""
    assert JOINT_DEFINITIONS[joint_name].flexion(180.0) == 0.0


def test_bending_a_knee_gives_positive_flexion() -> None:
    knee = JOINT_DEFINITIONS["knee"]

    assert knee.flexion(90.0) == 90.0
    assert knee.flexion(30.0) == 150.0


def test_a_hanging_arm_is_zero_shoulder_flexion_and_raising_it_is_positive() -> None:
    """The shoulder is the joint whose neutral is a closed angle, not an open one."""
    shoulder = JOINT_DEFINITIONS["shoulder"]

    assert shoulder.flexion(0.0) == 0.0
    assert shoulder.flexion(90.0) == 90.0


def test_a_standing_ankle_is_neutral_at_a_right_angle() -> None:
    ankle = JOINT_DEFINITIONS["ankle"]

    assert ankle.flexion(90.0) == 0.0
    assert ankle.flexion(70.0) == 20.0  # dorsiflexion
    assert ankle.flexion(120.0) == -30.0  # plantarflexion


# --- the human range -------------------------------------------------------


def test_gait_range_hip_flexion_is_plausible_and_the_fabricated_one_is_not() -> None:
    """The exact number that got through on 2026-08-30, now refused."""
    hip = JOINT_DEFINITIONS["hip"]

    assert hip.is_plausible(30.0)
    assert not hip.is_plausible(140.0)


def test_a_knee_does_not_bend_backwards_past_a_little() -> None:
    knee = JOINT_DEFINITIONS["knee"]

    assert knee.is_plausible(-5.0)
    assert not knee.is_plausible(-40.0)
    assert not knee.is_plausible(200.0)


# --- reading a joint off a set of landmarks --------------------------------


def standing_leg() -> dict[str, tuple[float, float, float]]:
    """A left leg standing straight: shoulder, hip, knee, ankle, toe."""
    return {
        "left_shoulder": (0.0, 1.4, 0.0),
        "left_hip": (0.0, 0.9, 0.0),
        "left_knee": (0.0, 0.5, 0.0),
        "left_ankle": (0.0, 0.1, 0.0),
        "left_foot_index": (0.2, 0.1, 0.0),
    }


def test_a_standing_leg_reads_as_neutral() -> None:
    landmarks = standing_leg()

    knee = joint_flexion(JOINT_DEFINITIONS["knee"], "left", landmarks)
    hip = joint_flexion(JOINT_DEFINITIONS["hip"], "left", landmarks)
    ankle = joint_flexion(JOINT_DEFINITIONS["ankle"], "left", landmarks)

    assert isclose(knee, 0.0, abs_tol=1e-6)
    assert isclose(hip, 0.0, abs_tol=1e-6)
    assert isclose(ankle, 0.0, abs_tol=1e-6)


def test_a_bent_knee_reads_as_flexion() -> None:
    landmarks = standing_leg()
    landmarks["left_ankle"] = (0.4, 0.5, 0.0)  # shin swung backwards, 90 degrees

    assert isclose(
        joint_flexion(JOINT_DEFINITIONS["knee"], "left", landmarks), 90.0, abs_tol=1e-6
    )


def test_a_missing_landmark_gives_no_reading_rather_than_a_default() -> None:
    landmarks = standing_leg()
    del landmarks["left_ankle"]

    assert joint_flexion(JOINT_DEFINITIONS["knee"], "left", landmarks) is None


def test_one_side_is_never_read_from_the_other_sides_landmarks() -> None:
    """Sides share no input, so two sides agreeing says something about the body."""
    landmarks = standing_leg()

    assert joint_flexion(JOINT_DEFINITIONS["knee"], "right", landmarks) is None


# --- the landmark set ------------------------------------------------------


def test_every_measurable_joint_names_landmarks_on_both_sides() -> None:
    names = required_landmarks()

    for joint_name in MEASURABLE_JOINTS:
        joint = JOINT_DEFINITIONS[joint_name]
        for side in ("left", "right"):
            for role in (joint.proximal, joint.center, joint.distal):
                assert landmark_name(side, role) in names


def test_the_measurable_joints_are_the_ones_a_gait_needs() -> None:
    assert set(MEASURABLE_JOINTS) == {"knee", "hip", "ankle", "shoulder", "elbow"}
