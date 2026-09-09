"""Build a joint-angle record out of pose landmarks, without touching a model.

Everything here is arithmetic over readings somebody else produced, so the
decisions this file makes can be read and tested without installing a pose
model or owning a video. The adapter that turns an actual file into readings
lives next door in `mediapipe_pose_source.py`.

Three rules shape it, and all three are the opposite of what the vision-model
path was caught doing:

- A reading the model was not confident about is dropped, not delivered with a
  caveat. The gap it leaves is visible downstream, because the observed-motion
  drawing breaks a stroke wherever time passes without a reading.
- An angle no human joint can reach is dropped and counted. It is not a
  measurement of the person in the video, whatever produced it.
- The two audits are both applied and neither can excuse the other. Surviving
  the fabrication checks does not make an impossible angle possible, and
  staying inside human range does not make a drawn curve a measurement.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from uuid import uuid4

from app.models.motion_analysis import JointVisibility, ObservedJointAngle
from app.models.pose_measurement import (
    PoseFrameReading,
    PoseMeasurementRecord,
    PoseMeasurementRequest,
)
from app.services.human_range_audit import audit_human_range, partition_by_human_range
from app.services.motion_evidence_audit import audit_motion_samples
from app.services.pose_landmark_geometry import (
    JOINT_DEFINITIONS,
    MEASURABLE_JOINTS,
    SIDES,
    joint_flexion,
    landmark_name,
)


# A landmark the model is this sure about is treated as plainly visible; below
# the lower bound it is treated as hidden. The band between them is the honest
# middle, and in real footage of a person walking every one of the three
# appears, because limbs pass behind the body.
CLEAR_VISIBILITY = 0.85
PARTIAL_VISIBILITY = 0.5

MAX_RETAINED_FRAMES = 2000
MAX_RETAINED_SAMPLES = 20000


class PoseSubjectRefused(ValueError):
    """Raised when measurement is asked for a subject that is not a person."""


def visibility_class(confidence: float) -> JointVisibility:
    """Map a landmark confidence onto the visibility the contract records."""
    if confidence >= CLEAR_VISIBILITY:
        return JointVisibility.CLEAR
    if confidence >= PARTIAL_VISIBILITY:
        return JointVisibility.PARTIAL
    return JointVisibility.OCCLUDED


def samples_from_frame(
    frame: PoseFrameReading,
    *,
    minimum_visibility: float,
    aspect_ratio: float = 1.0,
) -> tuple[list[ObservedJointAngle], int]:
    """Read every measurable joint out of one frame.

    Returns the readings and how many were dropped for low visibility. A joint
    is only read when all three of its landmarks cleared the floor, because an
    angle is only as trustworthy as its least visible corner.

    Coordinates arrive normalised separately across width and height, so on
    any frame that is not square a degree of x is not a degree of y. `x` is
    rescaled into units of image height before any angle is taken; skipping
    that silently tilts every joint on ordinary 16:9 footage.
    """
    positions = {
        reading.name: (reading.x * aspect_ratio, reading.y, 0.0)
        for reading in frame.landmarks
    }
    confidences = {reading.name: reading.visibility for reading in frame.landmarks}

    samples: list[ObservedJointAngle] = []
    dropped = 0
    for joint_name in MEASURABLE_JOINTS:
        definition = JOINT_DEFINITIONS[joint_name]
        roles = (definition.proximal, definition.center, definition.distal)
        for side in SIDES:
            names = [landmark_name(side, role) for role in roles]
            if any(name not in positions for name in names):
                continue
            confidence = min(confidences[name] for name in names)
            if confidence < minimum_visibility:
                dropped += 1
                continue
            flexion = joint_flexion(definition, side, positions)
            if flexion is None:
                continue
            samples.append(
                ObservedJointAngle(
                    timestamp_seconds=frame.timestamp_seconds,
                    joint_name=joint_name,
                    side=side,
                    angle_degrees=flexion,
                    confidence=confidence,
                    visibility=visibility_class(confidence),
                )
            )
    return samples, dropped


def build_pose_measurement(
    *,
    project_id: str,
    upload_id: str,
    source_sha256: str,
    model_name: str,
    model_sha256: str,
    request: PoseMeasurementRequest,
    frames: Iterable[PoseFrameReading],
    video_fps: float,
    frame_aspect_ratio: float = 1.0,
    video_duration_seconds: float,
    frames_sampled: int,
    elapsed_seconds: float,
    created_at: datetime | None = None,
) -> PoseMeasurementRecord:
    """Turn landmark readings into one audited measurement record."""
    if request.subject_is_human is not True:  # pragma: no cover - typed Literal
        raise PoseSubjectRefused(
            "This pose model assumes a human body plan and will not be used on "
            "another subject."
        )

    detected = list(frames)
    all_samples: list[ObservedJointAngle] = []
    dropped_low_visibility = 0
    for frame in detected:
        found, dropped = samples_from_frame(
            frame,
            minimum_visibility=request.minimum_visibility,
            aspect_ratio=frame_aspect_ratio,
        )
        all_samples.extend(found)
        dropped_low_visibility += dropped

    inside, outside = partition_by_human_range(all_samples)
    range_audit = audit_human_range(inside, outside)

    times = [sample.timestamp_seconds for sample in inside]
    span = (max(times) - min(times)) if times else 0.0
    confidences = [sample.confidence for sample in inside]
    joints = sorted({sample.joint_name for sample in inside})

    return PoseMeasurementRecord(
        measurement_id=f"pms_{uuid4().hex[:12]}",
        project_id=project_id,
        upload_id=upload_id,
        source_sha256=source_sha256,
        model_name=model_name,
        model_sha256=model_sha256,
        frame_aspect_ratio=frame_aspect_ratio,
        requested_fps=request.frames_per_second,
        window_start_seconds=request.window_start_seconds,
        window_end_seconds=request.window_start_seconds + request.window_seconds,
        video_fps=video_fps,
        video_duration_seconds=video_duration_seconds,
        frames_sampled=frames_sampled,
        frames_with_pose=len(detected),
        detection_ratio=(len(detected) / frames_sampled) if frames_sampled else 0.0,
        dropped_low_visibility=dropped_low_visibility,
        dropped_outside_human_range=len(outside),
        joint_names=joints,
        samples=inside[:MAX_RETAINED_SAMPLES],
        frames=detected[:MAX_RETAINED_FRAMES],
        sample_count=len(inside),
        distinct_joint_count=len({(s.side, s.joint_name) for s in inside}),
        observed_span_seconds=span,
        samples_per_second=(len(inside) / span) if span else 0.0,
        mean_confidence=(sum(confidences) / len(confidences)) if confidences else 0.0,
        clear_sample_count=sum(
            1 for sample in inside if sample.visibility is JointVisibility.CLEAR
        ),
        audit=audit_motion_samples(inside, window_seconds=request.window_seconds),
        range_audit=range_audit,
        elapsed_seconds=elapsed_seconds,
        created_at=created_at or datetime.now(timezone.utc),
    )
