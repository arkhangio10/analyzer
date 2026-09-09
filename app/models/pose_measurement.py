"""Contracts for measuring human joint angles from a video's own pixels.

The vision-model path asks a language model to report joint angles and gets
back prose-shaped numbers. It failed its deterministic audit twice, on two
subjects and two kinematic chains, so this path does something different in
kind: a pose model runs locally over the frames of a file the person supplied,
returns landmark positions with its own per-landmark confidence, and the joint
angles are computed from those positions by arithmetic this repository owns.

What that buys, written into the types rather than argued in a comment:

- `cloud_calls_made` is permanently zero and `sent_to_provider` permanently
  false. Nothing here reaches a provider, so nothing here costs money and
  nothing here hands somebody's own footage to a third party.
- `physically_measured` stays false. Landmarks estimated from pixels are still
  estimates. A different and better method of estimating is not a measurement,
  and the day this system touches a real goniometer or a motion-capture rig is
  the day that field is allowed to change.
- `subject_topology` names the body plan the landmark model assumes. It is a
  human topology, so this path refuses any other subject rather than mapping a
  quadruped onto a landmark set built for a person.

The samples are the same `ObservedJointAngle` the vision path produces, so the
same deterministic audit judges both. That is the point: the audit that
rejected the fabricated data is the audit this path has to survive.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.motion_analysis import MotionEvidenceAudit, ObservedJointAngle


class PoseLandmarkReading(BaseModel):
    """One landmark the pose model placed in one frame.

    Coordinates are normalised to the image: 0 to 1 across width and height.
    They are kept because a human labelling ground truth labels an image, not
    a metric skeleton, so this is the space the benchmark can compare in.
    """

    name: str = Field(min_length=1, max_length=40)
    x: float
    y: float
    visibility: float = Field(ge=0, le=1)


class PoseFrameReading(BaseModel):
    """Every landmark found in one sampled frame."""

    frame_index: int = Field(ge=0)
    timestamp_seconds: float = Field(ge=0)
    landmarks: list[PoseLandmarkReading] = Field(default_factory=list, max_length=40)


class HumanRangeFinding(BaseModel):
    """One joint that reported flexion a human joint cannot reach."""

    joint_name: str = Field(min_length=1, max_length=40)
    side: Literal["left", "right"]
    reading_count: int = Field(ge=0)
    outside_count: int = Field(ge=0)
    minimum_observed: float
    maximum_observed: float
    allowed_minimum: float
    allowed_maximum: float


class HumanRangeAudit(BaseModel):
    """Whether the angles fall inside what a human body can reach.

    This is the check the 2026-08-30 run needed and did not have. A reported
    hip flexion of 140 degrees was caught by a person reading the number;
    arithmetic should have caught it first. It is deliberately kept out of the
    shared motion audit, whose rules are counted twice -- once in Python over
    one analysis and once in SQL over the whole library -- so that the two
    paths cannot drift apart. This question is a different one, and it only
    has an answer once the subject is known to be a human body.
    """

    checked_reading_count: int = Field(ge=0)
    outside_reading_count: int = Field(ge=0)
    outside_ratio: float = Field(ge=0, le=1)
    findings: list[HumanRangeFinding] = Field(default_factory=list, max_length=20)
    within_human_range: bool


class PoseMeasurementRecord(BaseModel):
    """One local pose measurement of one uploaded video."""

    measurement_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    upload_id: str = Field(min_length=1)
    source_sha256: str = Field(min_length=64, max_length=64)

    measurement_method: Literal["pose_model_landmarks"] = "pose_model_landmarks"
    physically_measured: Literal[False] = False
    cloud_calls_made: Literal[0] = 0
    sent_to_provider: Literal[False] = False
    subject_topology: Literal["human_body_33_landmark"] = "human_body_33_landmark"
    subject_kind: Literal["human_body"] = "human_body"
    # Angles are read in the plane of the image. A single camera's depth
    # estimate is the least trustworthy thing it produces, so it is not used,
    # and the cost of that choice is stated instead of hidden: motion swinging
    # toward or away from the lens is under-measured, and the camera has to see
    # the movement side on for these angles to mean anything.
    measured_in_image_plane: Literal[True] = True
    frame_aspect_ratio: float = Field(
        default=1.0,
        gt=0,
        description=(
            "Frame width divided by height. Normalised coordinates are not "
            "square, so an angle read from them without this is wrong on any "
            "video that is not."
        ),
    )

    model_name: str = Field(min_length=1, max_length=120)
    model_sha256: str = Field(min_length=64, max_length=64)

    requested_fps: float = Field(gt=0, le=60)
    window_start_seconds: float = Field(ge=0)
    window_end_seconds: float = Field(ge=0)
    video_fps: float = Field(ge=0)
    video_duration_seconds: float = Field(ge=0)

    frames_sampled: int = Field(ge=0)
    frames_with_pose: int = Field(ge=0)
    detection_ratio: float = Field(ge=0, le=1)
    dropped_low_visibility: int = Field(ge=0)
    dropped_outside_human_range: int = Field(ge=0)

    joint_names: list[str] = Field(default_factory=list, max_length=40)
    samples: list[ObservedJointAngle] = Field(default_factory=list, max_length=20000)
    frames: list[PoseFrameReading] = Field(default_factory=list, max_length=2000)

    sample_count: int = Field(ge=0)
    distinct_joint_count: int = Field(ge=0)
    observed_span_seconds: float = Field(ge=0)
    samples_per_second: float = Field(ge=0)
    mean_confidence: float = Field(ge=0, le=1)
    clear_sample_count: int = Field(ge=0)

    audit: MotionEvidenceAudit
    range_audit: HumanRangeAudit

    elapsed_seconds: float = Field(ge=0)
    created_at: datetime

    @property
    def is_usable(self) -> bool:
        """Report whether both audits allow these angles to be used.

        Either audit failing is enough to refuse. Passing the fabrication
        checks does not make an impossible angle possible, and staying inside
        human range does not make a drawn curve a measurement.
        """
        return self.audit.is_usable and self.range_audit.within_human_range


class PoseMeasurementRequest(BaseModel):
    """A caller's instruction to measure an uploaded video locally.

    `subject_is_human` is required and must be true. The landmark model assumes
    a human body plan, so the caller has to say that is what the video shows.
    It is an assertion by a person, recorded as one, not a detection.
    """

    frames_per_second: float = Field(default=10.0, gt=0, le=60)
    window_start_seconds: float = Field(default=0.0, ge=0, le=3600)
    window_seconds: float = Field(default=12.0, gt=0, le=120)
    minimum_visibility: float = Field(default=0.5, ge=0, le=1)
    subject_is_human: Literal[True]
