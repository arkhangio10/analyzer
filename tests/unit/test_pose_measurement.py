"""Tests for the measured-pose path and the two audits it has to survive.

What these tests exercise is the pipeline, not the pose model: landmarks are
constructed here by forward kinematics from angles chosen in the test, so the
arithmetic, the dropping rules, and both audits are under test while nothing
depends on a model file or a video. Whether a real pose model produces
landmarks this well is a separate question, and only a real video answers it.

The test that matters most is the pair at the bottom: a sequence shaped like
real walking survives the audit that rejected the vision model's output, and a
sequence shaped like that output still fails on this path too.
"""

from __future__ import annotations

from math import cos, radians, sin

import pytest

from app.models.motion_analysis import JointVisibility, MotionEvidenceVerdict
from app.models.pose_measurement import (
    PoseFrameReading,
    PoseLandmarkReading,
    PoseMeasurementRequest,
)
from app.services.human_range_audit import (
    audit_human_range,
    partition_by_human_range,
)
from app.services.pose_measurement import (
    build_pose_measurement,
    samples_from_frame,
    visibility_class,
)


THIGH = 0.4
SHIN = 0.4
UPPER_ARM = 0.3
FOREARM = 0.3


def rotate(vector: tuple[float, float], degrees_: float) -> tuple[float, float]:
    angle = radians(degrees_)
    return (
        vector[0] * cos(angle) - vector[1] * sin(angle),
        vector[0] * sin(angle) + vector[1] * cos(angle),
    )


def leg_landmarks(
    side: str,
    hip_flexion: float,
    knee_flexion: float,
    visibility: float,
) -> list[PoseLandmarkReading]:
    """Place one leg's landmarks so it reads back at the requested angles."""
    hip = (0.0, 0.9)
    thigh = rotate((0.0, -1.0), hip_flexion)
    knee = (hip[0] + THIGH * thigh[0], hip[1] + THIGH * thigh[1])
    shin = rotate(thigh, -knee_flexion)
    ankle = (knee[0] + SHIN * shin[0], knee[1] + SHIN * shin[1])
    toe_direction = rotate(shin, 90.0)
    toe = (ankle[0] + 0.2 * toe_direction[0], ankle[1] + 0.2 * toe_direction[1])
    return [
        # The hip angle is measured from the shoulder down, so a leg on its own
        # is not enough to read one. The shoulder travels with the leg here.
        PoseLandmarkReading(
            name=f"{side}_shoulder", x=0.0, y=1.4, visibility=visibility
        ),
        PoseLandmarkReading(name=f"{side}_hip", x=hip[0], y=hip[1], visibility=visibility),
        PoseLandmarkReading(name=f"{side}_knee", x=knee[0], y=knee[1], visibility=visibility),
        PoseLandmarkReading(name=f"{side}_ankle", x=ankle[0], y=ankle[1], visibility=visibility),
        PoseLandmarkReading(
            name=f"{side}_foot_index", x=toe[0], y=toe[1], visibility=visibility
        ),
    ]


def arm_landmarks(
    side: str,
    shoulder_flexion: float,
    elbow_flexion: float,
    visibility: float,
) -> list[PoseLandmarkReading]:
    """Place one arm's landmarks, plus the shoulder the hip angle needs."""
    shoulder = (0.0, 1.4)
    upper = rotate((0.0, -1.0), shoulder_flexion)
    elbow = (shoulder[0] + UPPER_ARM * upper[0], shoulder[1] + UPPER_ARM * upper[1])
    lower = rotate(upper, -elbow_flexion)
    wrist = (elbow[0] + FOREARM * lower[0], elbow[1] + FOREARM * lower[1])
    return [
        PoseLandmarkReading(
            name=f"{side}_shoulder", x=shoulder[0], y=shoulder[1], visibility=visibility
        ),
        PoseLandmarkReading(name=f"{side}_elbow", x=elbow[0], y=elbow[1], visibility=visibility),
        PoseLandmarkReading(name=f"{side}_wrist", x=wrist[0], y=wrist[1], visibility=visibility),
    ]


def walking_frames(
    count: int = 60,
    fps: float = 10.0,
    mirrored: bool = False,
    constant_confidence: bool = False,
) -> list[PoseFrameReading]:
    """A gait: two legs in antiphase, cycling about once a second.

    `mirrored` and `constant_confidence` reproduce the two shapes the vision
    model returned, so the same pipeline can be shown to refuse them.
    """
    frames: list[PoseFrameReading] = []
    for index in range(count):
        phase = (index / fps) * 360.0  # one cycle per second
        opposite = phase if mirrored else phase + 180.0
        landmarks: list[PoseLandmarkReading] = []
        for side, angle in (("left", phase), ("right", opposite)):
            # A limb passing behind the body is seen less well than one in front.
            visibility = (
                0.8 if constant_confidence else 0.6 + 0.35 * (0.5 + 0.5 * sin(radians(angle)))
            )
            visibility = min(0.99, visibility)
            landmarks += leg_landmarks(
                side,
                hip_flexion=25.0 * sin(radians(angle)),
                knee_flexion=32.0 + 28.0 * sin(radians(angle + 90.0)),
                visibility=visibility,
            )
            landmarks += arm_landmarks(
                side,
                shoulder_flexion=20.0 * sin(radians(angle + 180.0)),
                elbow_flexion=25.0 + 20.0 * sin(radians(angle)),
                visibility=visibility,
            )
        frames.append(
            PoseFrameReading(
                frame_index=index,
                timestamp_seconds=round(index / fps, 3),
                landmarks=landmarks,
            )
        )
    return frames


def request(**overrides: object) -> PoseMeasurementRequest:
    values: dict[str, object] = {"subject_is_human": True, "window_seconds": 6.0}
    values.update(overrides)
    return PoseMeasurementRequest(**values)


def measure(frames: list[PoseFrameReading], **overrides: object):
    return build_pose_measurement(
        project_id="prj_test",
        upload_id="upl_test",
        source_sha256="a" * 64,
        model_name="pose_landmarker_lite",
        model_sha256="b" * 64,
        request=request(**overrides),
        frames=frames,
        video_fps=30.0,
        video_duration_seconds=8.0,
        frames_sampled=len(frames),
        elapsed_seconds=1.5,
    )


# --- visibility ------------------------------------------------------------


def test_visibility_is_banded_rather_than_reported_as_one_word() -> None:
    assert visibility_class(0.95) is JointVisibility.CLEAR
    assert visibility_class(0.6) is JointVisibility.PARTIAL
    assert visibility_class(0.2) is JointVisibility.OCCLUDED


def test_a_joint_takes_the_confidence_of_its_least_visible_corner() -> None:
    frame = PoseFrameReading(
        frame_index=0,
        timestamp_seconds=0.0,
        landmarks=[
            PoseLandmarkReading(name="left_hip", x=0.0, y=0.9, visibility=0.95),
            PoseLandmarkReading(name="left_knee", x=0.0, y=0.5, visibility=0.55),
            PoseLandmarkReading(name="left_ankle", x=0.0, y=0.1, visibility=0.9),
        ],
        )

    samples, _ = samples_from_frame(frame, minimum_visibility=0.5)

    knee = next(s for s in samples if s.joint_name == "knee")
    assert knee.confidence == 0.55
    assert knee.visibility is JointVisibility.PARTIAL


def test_a_reading_below_the_floor_is_dropped_and_counted() -> None:
    frame = PoseFrameReading(
        frame_index=0,
        timestamp_seconds=0.0,
        landmarks=[
            PoseLandmarkReading(name="left_hip", x=0.0, y=0.9, visibility=0.9),
            PoseLandmarkReading(name="left_knee", x=0.0, y=0.5, visibility=0.1),
            PoseLandmarkReading(name="left_ankle", x=0.0, y=0.1, visibility=0.9),
        ],
    )

    samples, dropped = samples_from_frame(frame, minimum_visibility=0.5)

    assert [s.joint_name for s in samples] == []
    assert dropped == 1


def test_a_joint_missing_a_landmark_is_skipped_without_counting_as_dropped() -> None:
    """Absent is not the same as seen badly, and the counts say which."""
    frame = PoseFrameReading(
        frame_index=0,
        timestamp_seconds=0.0,
        landmarks=[
            PoseLandmarkReading(name="left_hip", x=0.0, y=0.9, visibility=0.9),
            PoseLandmarkReading(name="left_knee", x=0.0, y=0.5, visibility=0.9),
        ],
    )

    samples, dropped = samples_from_frame(frame, minimum_visibility=0.5)

    assert samples == []
    assert dropped == 0


# --- the human range -------------------------------------------------------


def test_the_fabricated_hip_angle_is_partitioned_out() -> None:
    frames = walking_frames(count=20)
    good = measure(frames)
    assert good.dropped_outside_human_range == 0

    impossible = [
        PoseFrameReading(
            frame_index=index,
            timestamp_seconds=index / 10,
            landmarks=leg_landmarks("left", hip_flexion=140.0, knee_flexion=10.0, visibility=0.9),
        )
        for index in range(20)
    ]

    refused = measure(impossible)

    assert refused.dropped_outside_human_range > 0
    assert refused.range_audit.within_human_range is False
    assert refused.is_usable is False
    hip = next(f for f in refused.range_audit.findings if f.joint_name == "hip")
    assert hip.allowed_maximum == 130.0
    assert hip.maximum_observed > 130.0


def test_nothing_measured_is_not_the_same_as_within_range() -> None:
    audit = audit_human_range([], [])

    assert audit.checked_reading_count == 0
    assert audit.within_human_range is False


def test_a_joint_with_no_declared_range_is_kept_rather_than_guessed_at() -> None:
    from app.models.motion_analysis import ObservedJointAngle

    sample = ObservedJointAngle(
        timestamp_seconds=0.0,
        joint_name="pelvis",
        side="center",
        angle_degrees=980.0,
        confidence=0.9,
        visibility=JointVisibility.CLEAR,
    )

    inside, outside = partition_by_human_range([sample])

    assert inside == [sample]
    assert outside == []


def test_a_few_impossible_frames_do_not_void_a_long_reading() -> None:
    """A tracker losing a limb for a moment is not a fabricated sequence."""
    frames = walking_frames(count=60)
    frames.append(
        PoseFrameReading(
            frame_index=60,
            timestamp_seconds=6.0,
            landmarks=leg_landmarks("left", hip_flexion=145.0, knee_flexion=5.0, visibility=0.9),
        )
    )

    record = measure(frames)

    assert record.dropped_outside_human_range > 0
    assert record.range_audit.within_human_range is True


# --- what the record claims ------------------------------------------------


def test_the_record_never_claims_a_measurement_a_payment_or_a_provider() -> None:
    record = measure(walking_frames())

    assert record.physically_measured is False
    assert record.cloud_calls_made == 0
    assert record.sent_to_provider is False
    assert record.measurement_method == "pose_model_landmarks"
    assert record.subject_topology == "human_body_33_landmark"


def test_the_record_reports_which_model_produced_it() -> None:
    record = measure(walking_frames())

    assert record.model_name == "pose_landmarker_lite"
    assert record.model_sha256 == "b" * 64


def test_the_counts_are_recomputable_from_the_samples() -> None:
    record = measure(walking_frames(count=40))

    assert record.sample_count == len(record.samples)
    assert record.distinct_joint_count == len(
        {(s.side, s.joint_name) for s in record.samples}
    )
    assert record.frames_with_pose == 40
    assert record.detection_ratio == 1.0
    assert set(record.joint_names) == {"knee", "hip", "ankle", "shoulder", "elbow"}


def test_frames_the_model_found_no_pose_in_lower_the_detection_ratio() -> None:
    record = build_pose_measurement(
        project_id="prj_test",
        upload_id="upl_test",
        source_sha256="a" * 64,
        model_name="pose_landmarker_lite",
        model_sha256="b" * 64,
        request=request(),
        frames=walking_frames(count=30),
        video_fps=30.0,
        video_duration_seconds=8.0,
        frames_sampled=60,
        elapsed_seconds=1.0,
    )

    assert record.frames_with_pose == 30
    assert record.detection_ratio == 0.5


# --- the audit that rejected the vision model ------------------------------


def test_a_gait_shaped_reading_survives_the_audit_that_rejected_the_model() -> None:
    """The whole point of P3.2, stated as one assertion.

    The samples here are not a model's answer about a video; they are computed
    from positions by the same arithmetic that will run on real landmarks. Two
    legs move in antiphase, confidence varies with how well a limb is seen,
    and every joint cycles. That is what the audit was written to look for.
    """
    record = measure(walking_frames(count=60))

    assert record.audit.verdict is MotionEvidenceVerdict.USABLE
    assert record.audit.findings == []
    assert record.audit.mirrored_frame_ratio < 0.8
    assert record.audit.distinct_confidence_values > 1
    assert record.audit.acyclic_joints == []
    assert record.range_audit.within_human_range is True
    assert record.is_usable is True


def test_the_same_pipeline_still_refuses_the_shape_the_model_returned() -> None:
    """Mirrored sides and one confidence for everything, measured locally."""
    record = measure(
        walking_frames(count=60, mirrored=True, constant_confidence=True)
    )

    codes = {finding.code.value for finding in record.audit.findings}
    assert "mirrored_sides" in codes
    assert "uniform_confidence" in codes
    assert record.audit.verdict is MotionEvidenceVerdict.NOT_EVIDENCE
    assert record.is_usable is False


def test_passing_one_audit_does_not_excuse_the_other() -> None:
    """Cyclic, varied, independent -- and still anatomically impossible."""
    frames = walking_frames(count=60)
    for frame in frames:
        for landmark in frame.landmarks:
            if landmark.name.endswith("_ankle"):
                # Drag every ankle far behind the knee: the knee reads as bent
                # past what a knee bends, while the motion stays cyclic.
                landmark.x -= 0.75

    record = measure(frames)

    assert record.range_audit.within_human_range is False
    assert record.is_usable is False


def test_a_measurement_costs_nothing_so_it_carries_no_usage(monkeypatch) -> None:
    record = measure(walking_frames(count=20))

    assert not hasattr(record, "usage")
    assert record.cloud_calls_made == 0
