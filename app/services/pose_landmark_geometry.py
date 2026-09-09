"""Turn human pose landmarks into joint angles, with a stated convention.

This is the arithmetic half of the measured-pose path, kept apart from the
model that produces landmarks so it can be read and tested without one.

Two things here are anatomy, not code style, and both are written as data so a
reader can disagree with a number rather than with a formula:

- A three-point interior angle is not a joint angle. A straight knee reads
  180 degrees and a straight knee is zero flexion, so every joint carries the
  interior angle it shows in the neutral standing pose and the direction
  flexion moves from there.
- A joint has a range a human body can reach. Angles outside it are not
  measurements of a person, whatever produced them, and saying so is the check
  that the 2026-08-30 run needed and did not have: a reported hip flexion of
  140 degrees was caught by a person reading the number, not by the system.

Sides are computed from different landmarks on purpose. Left and right never
share an input here, so two sides agreeing is evidence about the body rather
than an artefact of the calculation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, degrees, isfinite, sqrt


# --- landmark names -------------------------------------------------------
# The subset this module needs, named rather than indexed, so a change in the
# provider's ordering cannot silently rotate a body.

LEFT_SHOULDER = "left_shoulder"
RIGHT_SHOULDER = "right_shoulder"
LEFT_ELBOW = "left_elbow"
RIGHT_ELBOW = "right_elbow"
LEFT_WRIST = "left_wrist"
RIGHT_WRIST = "right_wrist"
LEFT_HIP = "left_hip"
RIGHT_HIP = "right_hip"
LEFT_KNEE = "left_knee"
RIGHT_KNEE = "right_knee"
LEFT_ANKLE = "left_ankle"
RIGHT_ANKLE = "right_ankle"
LEFT_FOOT_INDEX = "left_foot_index"
RIGHT_FOOT_INDEX = "right_foot_index"


Point = tuple[float, float, float]


@dataclass(frozen=True)
class JointDefinition:
    """One measurable joint: three landmarks, a neutral pose, and a range.

    `neutral_degrees` is the interior angle the three points form when the
    person stands still with arms at their sides. `sign` is +1 when flexion
    opens that interior angle and -1 when flexion closes it. Together they
    turn a raw interior angle into the flexion convention the rest of the
    system already uses: zero is neutral standing and flexion is positive.

    `minimum_degrees` and `maximum_degrees` are generous clinical ranges for
    that flexion. They are wide on purpose -- the check is meant to catch a
    number no body could produce, not to referee an athlete.
    """

    name: str
    proximal: str
    center: str
    distal: str
    neutral_degrees: float
    sign: int
    minimum_degrees: float
    maximum_degrees: float

    def flexion(self, interior_degrees: float) -> float:
        """Convert an interior angle into flexion under this convention."""
        return self.sign * (interior_degrees - self.neutral_degrees)

    def is_plausible(self, flexion_degrees: float) -> bool:
        """Report whether a human joint can reach this flexion."""
        return self.minimum_degrees <= flexion_degrees <= self.maximum_degrees


# Neutral values describe a person standing upright, arms hanging down.
#   knee, elbow, hip: the three points are nearly in line, so 180 degrees.
#   shoulder: the hip and the elbow are both below the shoulder, so the
#             interior angle is near zero and raising the arm opens it.
#   ankle: the shin and the foot are near a right angle.
_JOINTS: tuple[JointDefinition, ...] = (
    JointDefinition("knee", "hip", "knee", "ankle", 180.0, -1, -10.0, 150.0),
    JointDefinition("hip", "shoulder", "hip", "knee", 180.0, -1, -30.0, 130.0),
    JointDefinition("ankle", "knee", "ankle", "foot_index", 90.0, -1, -50.0, 30.0),
    JointDefinition("shoulder", "hip", "shoulder", "elbow", 0.0, 1, -60.0, 180.0),
    JointDefinition("elbow", "shoulder", "elbow", "wrist", 180.0, -1, -10.0, 150.0),
)

JOINT_DEFINITIONS: dict[str, JointDefinition] = {
    joint.name: joint for joint in _JOINTS
}

MEASURABLE_JOINTS: tuple[str, ...] = tuple(joint.name for joint in _JOINTS)

SIDES: tuple[str, ...] = ("left", "right")


def landmark_name(side: str, role: str) -> str:
    """Name the landmark this side uses for one role in a joint."""
    return f"{side}_{role}"


def required_landmarks() -> frozenset[str]:
    """Every landmark any measurable joint needs, on either side."""
    names: set[str] = set()
    for joint in _JOINTS:
        for side in SIDES:
            for role in (joint.proximal, joint.center, joint.distal):
                names.add(landmark_name(side, role))
    return frozenset(names)


def _subtract(first: Point, second: Point) -> Point:
    return (first[0] - second[0], first[1] - second[1], first[2] - second[2])


def _norm(vector: Point) -> float:
    return sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)


def interior_angle(
    proximal: Point,
    center: Point,
    distal: Point,
) -> float | None:
    """Return the angle at `center`, in degrees, or None if it is undefined.

    Two landmarks reported at the same position give a zero-length vector and
    no angle. That is a missing reading, and it is returned as one rather than
    resolved to a default that would look like a measurement.
    """
    first = _subtract(proximal, center)
    second = _subtract(distal, center)
    first_length = _norm(first)
    second_length = _norm(second)
    if first_length == 0 or second_length == 0:
        return None
    dot = sum(a * b for a, b in zip(first, second))
    cosine = dot / (first_length * second_length)
    # Floating point can push a legitimate cosine just past the domain of acos.
    cosine = max(-1.0, min(1.0, cosine))
    angle = degrees(acos(cosine))
    return angle if isfinite(angle) else None


def joint_flexion(
    joint: JointDefinition,
    side: str,
    landmarks: dict[str, Point],
) -> float | None:
    """Return this side's flexion for one joint, or None when a point is absent.

    A missing landmark produces no reading. It is never filled in from the
    other side, from the previous frame, or from the neutral pose.
    """
    try:
        points = tuple(
            landmarks[landmark_name(side, role)]
            for role in (joint.proximal, joint.center, joint.distal)
        )
    except KeyError:
        return None
    interior = interior_angle(*points)
    if interior is None:
        return None
    return joint.flexion(interior)
