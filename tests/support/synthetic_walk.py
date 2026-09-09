"""Render a walking figure at angles chosen by the caller.

This exists so the measured-pose path can be tested end to end without a real
video: the angles going in are known exactly, so the angles coming out can be
compared with them.

What it is not, and must never be turned into, is validation. Whoever draws
the figure decides both the question and the answer, so a measurement scored
against it is scored against its own author. That is the failure mode the
whole benchmark exists to prevent, which is why this lives in `tests/` and not
in `data/pose-benchmarks/`, and why nothing here can produce a
`PoseBenchmarkCase` -- those are `authored_by: Literal["person"]`.

What it does establish is worth having: that a real detector, a real decoder,
the flexion convention, the aspect correction and the audit all agree with
each other on input whose truth is not in question.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path


WIDTH, HEIGHT = 640, 720
SKIN = (170, 190, 215)
SHIRT = (90, 70, 60)
TROUSER = (70, 55, 45)
FAR_LEG = (60, 48, 40)
FAR_ARM = (78, 60, 52)

# The two hips are drawn a little apart, and the two shoulders too. Hanging
# both legs off one point gives the detector nothing to tell them apart with,
# and it then invents a separation -- which looks like a measurement and is not.
HIP_LEFT = (332.0, 400.0)
HIP_RIGHT = (308.0, 400.0)
SHOULDER_LEFT = (330.0, 240.0)
SHOULDER_RIGHT = (310.0, 240.0)
THIGH, SHIN, UPPER_ARM, FOREARM = 110.0, 110.0, 85.0, 80.0


@dataclass(frozen=True)
class Pose:
    """The angles one rendered frame was drawn at, in the flexion convention."""

    hip_left: float
    knee_left: float
    hip_right: float
    knee_right: float
    shoulder_left: float
    elbow_left: float
    shoulder_right: float
    elbow_right: float


def walking_pose(seconds: float, cadence_hz: float = 1.0) -> Pose:
    """A gait at one cycle per second: legs in antiphase, arms opposing them."""
    phase = 360.0 * cadence_hz * seconds
    other = phase + 180.0
    radians = math.radians

    def hip(angle: float) -> float:
        return 22.0 * math.sin(radians(angle))

    def knee(angle: float) -> float:
        return 30.0 + 25.0 * math.sin(radians(angle + 90.0))

    return Pose(
        hip_left=hip(phase),
        knee_left=knee(phase),
        hip_right=hip(other),
        knee_right=knee(other),
        shoulder_left=18.0 * math.sin(radians(other)),
        elbow_left=25.0 + 15.0 * math.sin(radians(other)),
        shoulder_right=18.0 * math.sin(radians(phase)),
        elbow_right=25.0 + 15.0 * math.sin(radians(phase)),
    )


def _rotate(vector, degrees: float):
    angle = math.radians(degrees)
    return (
        vector[0] * math.cos(angle) - vector[1] * math.sin(angle),
        vector[0] * math.sin(angle) + vector[1] * math.cos(angle),
    )


def render(pose: Pose):
    """Draw one frame. Returns a BGR array; needs OpenCV and NumPy."""
    import cv2
    import numpy

    image = numpy.full((HEIGHT, WIDTH, 3), 210, numpy.uint8)
    cv2.rectangle(image, (0, 600), (WIDTH, HEIGHT), (150, 160, 170), -1)

    def limb(start, end, width, colour):
        cv2.line(
            image,
            (int(start[0]), int(start[1])),
            (int(end[0]), int(end[1])),
            colour,
            width,
            cv2.LINE_AA,
        )
        cv2.circle(image, (int(end[0]), int(end[1])), width // 2, colour, -1, cv2.LINE_AA)

    def leg(hip_flexion: float, knee_flexion: float, colour, origin):
        thigh = _rotate((0, 1), -hip_flexion)
        knee = (origin[0] + THIGH * thigh[0], origin[1] + THIGH * thigh[1])
        shin = _rotate(thigh, knee_flexion)
        ankle = (knee[0] + SHIN * shin[0], knee[1] + SHIN * shin[1])
        limb(origin, knee, 34, colour)
        limb(knee, ankle, 28, colour)
        cv2.line(
            image,
            (int(ankle[0]), int(ankle[1])),
            (int(ankle[0] + 38), int(ankle[1] + 6)),
            (50, 45, 45),
            18,
            cv2.LINE_AA,
        )

    def arm(shoulder_flexion: float, elbow_flexion: float, colour, origin):
        upper = _rotate((0, 1), -shoulder_flexion)
        elbow = (origin[0] + UPPER_ARM * upper[0], origin[1] + UPPER_ARM * upper[1])
        lower = _rotate(upper, elbow_flexion)
        wrist = (elbow[0] + FOREARM * lower[0], elbow[1] + FOREARM * lower[1])
        limb(origin, elbow, 26, colour)
        limb(elbow, wrist, 22, SKIN)

    # Far side first, then the torso, then the near side, so the body occludes
    # the limb behind it the way a real one does.
    leg(pose.hip_right, pose.knee_right, FAR_LEG, HIP_RIGHT)
    arm(pose.shoulder_right, pose.elbow_right, FAR_ARM, SHOULDER_RIGHT)
    cv2.rectangle(image, (272, 236), (368, 410), SHIRT, -1, cv2.LINE_AA)
    cv2.ellipse(image, (320, 400), (52, 34), 0, 0, 360, TROUSER, -1, cv2.LINE_AA)
    leg(pose.hip_left, pose.knee_left, TROUSER, HIP_LEFT)
    arm(pose.shoulder_left, pose.elbow_left, SHIRT, SHOULDER_LEFT)
    cv2.circle(image, (320, 195), 46, SKIN, -1, cv2.LINE_AA)
    cv2.circle(image, (320, 152), 40, (40, 35, 32), -1, cv2.LINE_AA)
    cv2.circle(image, (303, 190), 5, (30, 30, 30), -1, cv2.LINE_AA)
    cv2.circle(image, (337, 190), 5, (30, 30, 30), -1, cv2.LINE_AA)
    cv2.line(image, (306, 212), (334, 212), (110, 100, 130), 3, cv2.LINE_AA)
    cv2.line(image, (284, 240), (356, 240), SKIN, 20, cv2.LINE_AA)
    return image


def write_walk(
    path: Path | str,
    *,
    seconds: float = 6.0,
    fps: float = 30.0,
    cadence_hz: float = 1.0,
) -> list[tuple[float, Pose]]:
    """Write a walking clip and return the angles each frame was drawn at."""
    import cv2

    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (WIDTH, HEIGHT)
    )
    truth: list[tuple[float, Pose]] = []
    for index in range(int(seconds * fps)):
        moment = index / fps
        pose = walking_pose(moment, cadence_hz)
        writer.write(render(pose))
        truth.append((moment, pose))
    writer.release()
    return truth
