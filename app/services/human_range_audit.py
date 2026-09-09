"""Check reported flexion against what a human joint can actually reach.

The shared motion audit catches fabrication by its shape: both sides moving
identically, one confidence for every sample, a single arc where a gait cycle
belongs. It does not ask whether a number is anatomically possible, and on
2026-08-30 that gap showed: a hip flexion of 140 degrees passed every shape
check and was caught by a person reading it. Human hip flexion in gait is
about 30 degrees.

This module asks only that question, and is kept out of `verdict_from_counts`
on purpose. Those rules are counted twice -- once in Python over a single
analysis, once in SQL over the whole library -- and the value of that pairing
is that a disagreement is unambiguously a counting bug. Adding a rule here
would mean adding it there too, and this question is a different one: it has
an answer only once the subject is known to be a human body.

Readings outside the range are not returned to callers. An angle no body can
reach is not a measurement of that body, so it is dropped and counted rather
than delivered with a caveat.
"""

from __future__ import annotations

from collections import defaultdict

from app.models.motion_analysis import ObservedJointAngle
from app.models.pose_measurement import HumanRangeAudit, HumanRangeFinding
from app.services.pose_landmark_geometry import JOINT_DEFINITIONS


# A few impossible readings in a long sequence are a tracker losing a limb for
# a moment. A large share of them means the thing being measured is not a
# human body, or the numbers did not come from one.
MAX_OUTSIDE_RATIO = 0.05


def partition_by_human_range(
    samples: list[ObservedJointAngle],
) -> tuple[list[ObservedJointAngle], list[ObservedJointAngle]]:
    """Split samples into those a human joint can reach and those it cannot.

    A joint this module has no range for is kept. Silence about a joint is not
    permission to invent a limit for it.
    """
    inside: list[ObservedJointAngle] = []
    outside: list[ObservedJointAngle] = []
    for sample in samples:
        definition = JOINT_DEFINITIONS.get(sample.joint_name)
        if definition is None or definition.is_plausible(sample.angle_degrees):
            inside.append(sample)
        else:
            outside.append(sample)
    return inside, outside


def audit_human_range(
    inside: list[ObservedJointAngle],
    outside: list[ObservedJointAngle],
) -> HumanRangeAudit:
    """Report how much of the reading was outside a human range, and where."""
    checked = len(inside) + len(outside)
    if checked == 0:
        return HumanRangeAudit(
            checked_reading_count=0,
            outside_reading_count=0,
            outside_ratio=0.0,
            findings=[],
            # Nothing was measured, so nothing may be called human. An empty
            # reading is not a passing one.
            within_human_range=False,
        )

    grouped: dict[tuple[str, str], list[ObservedJointAngle]] = defaultdict(list)
    for sample in inside + outside:
        if sample.side in ("left", "right"):
            grouped[(sample.joint_name, sample.side)].append(sample)

    offending = {
        (sample.joint_name, sample.side)
        for sample in outside
        if sample.side in ("left", "right")
    }

    findings: list[HumanRangeFinding] = []
    for key in sorted(offending):
        joint_name, side = key
        definition = JOINT_DEFINITIONS[joint_name]
        readings = grouped[key]
        angles = [sample.angle_degrees for sample in readings]
        findings.append(
            HumanRangeFinding(
                joint_name=joint_name,
                side=side,
                reading_count=len(readings),
                outside_count=sum(
                    1 for sample in readings if not definition.is_plausible(sample.angle_degrees)
                ),
                minimum_observed=min(angles),
                maximum_observed=max(angles),
                allowed_minimum=definition.minimum_degrees,
                allowed_maximum=definition.maximum_degrees,
            )
        )

    ratio = len(outside) / checked
    return HumanRangeAudit(
        checked_reading_count=checked,
        outside_reading_count=len(outside),
        outside_ratio=ratio,
        findings=findings[:20],
        within_human_range=ratio <= MAX_OUTSIDE_RATIO,
    )
