"""Tests for the arithmetic that decides whether samples were measured."""

import math

from app.models.motion_analysis import (
    JointVisibility,
    MotionAuditCode,
    MotionEvidenceVerdict,
    ObservedJointAngle,
)
from app.services.motion_evidence_audit import audit_motion_samples


def sample(
    time: float,
    joint: str,
    side: str,
    angle: float,
    confidence: float = 0.7,
    visibility: JointVisibility = JointVisibility.CLEAR,
) -> ObservedJointAngle:
    return ObservedJointAngle(
        timestamp_seconds=time,
        joint_name=joint,
        side=side,
        angle_degrees=angle,
        confidence=confidence,
        visibility=visibility,
    )


def walking_like(frames: int = 48) -> list[ObservedJointAngle]:
    """Build samples with the properties real gait has: cyclic and antiphase."""
    samples: list[ObservedJointAngle] = []
    for index in range(frames):
        time = round(index * 0.25, 3)
        phase = index * 0.5
        for joint, amplitude in (("hip", 25.0), ("knee", 30.0)):
            samples.append(
                sample(
                    time,
                    joint,
                    "left",
                    round(amplitude * math.sin(phase), 2),
                    confidence=round(0.5 + 0.4 * abs(math.cos(phase)), 3),
                    visibility=(
                        JointVisibility.CLEAR
                        if index % 3
                        else JointVisibility.PARTIAL
                    ),
                )
            )
            samples.append(
                sample(
                    time,
                    joint,
                    "right",
                    round(amplitude * math.sin(phase + math.pi), 2),
                    confidence=round(0.5 + 0.3 * abs(math.sin(phase)), 3),
                    visibility=(
                        JointVisibility.CLEAR
                        if index % 4
                        else JointVisibility.OCCLUDED
                    ),
                )
            )
    return samples


def drawn_curve() -> list[ObservedJointAngle]:
    """Reproduce the shape a real provider call returned for a walking video.

    Both sides identical, one confidence for everything, one visibility for
    everything, and a single triangular ramp across the whole window.
    """
    samples: list[ObservedJointAngle] = []
    for index in range(49):
        time = round(60 + index * 0.25, 3)
        angle = 10.0 + 5.0 * (index if index <= 28 else 56 - index)
        for side in ("left", "right"):
            samples.append(
                sample(
                    time,
                    "hip",
                    side,
                    angle,
                    confidence=0.7,
                    visibility=JointVisibility.PARTIAL,
                )
            )
    return samples


def test_real_gait_shaped_samples_are_accepted() -> None:
    audit = audit_motion_samples(walking_like(), window_seconds=12.0)

    assert audit.verdict is MotionEvidenceVerdict.USABLE
    assert audit.is_usable is True
    assert audit.findings == []
    assert audit.mirrored_frame_ratio < 0.8
    assert audit.acyclic_joints == []


def test_the_pattern_the_provider_actually_returned_is_rejected() -> None:
    audit = audit_motion_samples(drawn_curve(), window_seconds=12.0)

    assert audit.verdict is MotionEvidenceVerdict.NOT_EVIDENCE
    assert audit.is_usable is False
    assert audit.mirrored_frame_ratio == 1.0
    assert audit.distinct_confidence_values == 1
    assert audit.distinct_visibility_values == 1
    assert audit.acyclic_joints == ["left.hip", "right.hip"]
    assert len(audit.findings) >= 3
    codes = {item.code for item in audit.findings}
    assert MotionAuditCode.MIRRORED_SIDES in codes
    assert MotionAuditCode.UNIFORM_CONFIDENCE in codes
    assert MotionAuditCode.UNIFORM_VISIBILITY in codes
    assert MotionAuditCode.ACYCLIC_ALL in codes


def test_one_flag_alone_is_only_suspect() -> None:
    samples = [
        item.model_copy(update={"confidence": 0.7})
        for item in walking_like()
    ]

    audit = audit_motion_samples(samples, window_seconds=12.0)

    assert audit.verdict is MotionEvidenceVerdict.SUSPECT
    assert audit.is_usable is False
    assert len(audit.findings) == 1


def test_findings_state_counts_a_reader_can_recompute() -> None:
    audit = audit_motion_samples(drawn_curve(), window_seconds=12.0)

    mirrored = next(
        item for item in audit.findings
        if item.code is MotionAuditCode.MIRRORED_SIDES
    )
    assert mirrored.values == {"identical": "49", "paired": "49"}
    assert "49 of 49" in mirrored.message

    confidence = next(
        item for item in audit.findings
        if item.code is MotionAuditCode.UNIFORM_CONFIDENCE
    )
    assert confidence.values == {"samples": "98", "confidence": "0.7"}
    assert "98 samples" in confidence.message


def test_an_empty_analysis_is_never_evidence() -> None:
    audit = audit_motion_samples([], window_seconds=12.0)

    assert audit.verdict is MotionEvidenceVerdict.NOT_EVIDENCE
    assert audit.checked_joint_count == 0
    assert [item.code for item in audit.findings] == [MotionAuditCode.NO_SAMPLES]
    assert audit.findings[0].message == (
        "The analysis returned no usable joint samples."
    )


def test_a_narrow_swing_is_not_called_acyclic() -> None:
    """A joint that barely moves has no cycle to look for, so it is not flagged."""
    samples = [
        sample(round(index * 0.25, 3), "wrist", "center", 2.0 + index * 0.1)
        for index in range(20)
    ]

    audit = audit_motion_samples(samples, window_seconds=5.0)

    assert audit.acyclic_joints == []
    assert audit.checked_joint_count == 1


def test_a_handful_of_samples_is_too_little_to_condemn() -> None:
    """Below its thresholds the audit stays silent rather than guessing."""
    samples = [
        sample(0.0, "hip", "left", 5.0),
        sample(0.0, "hip", "right", 5.0),
        sample(0.25, "hip", "left", 6.0),
        sample(0.25, "hip", "right", 6.0),
    ]

    audit = audit_motion_samples(samples, window_seconds=1.0)

    assert audit.verdict is MotionEvidenceVerdict.USABLE
    assert audit.mirrored_frame_ratio == 1.0
    assert audit.findings == []
