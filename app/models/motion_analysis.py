"""Contracts for higher-frame-rate motion analysis of an approved video.

The procedure extraction pass reads a video as instruction and returns prose:
"push off with the hips". That sentence can never become a trajectory. This
pass reads the same approved video as *movement* and returns timestamped joint
angles at a stated sampling rate, so the gap between a description and a
trajectory becomes measurable instead of rhetorical.

Three honesty rules shape these contracts:

- Angles estimated by a vision model are estimates, not measurements.
  `measurement_method` and `physically_measured` say so permanently, and every
  sample carries its own confidence and visibility.
- Observing a human body is not the same as commanding a robot. The observed
  kinematic chain is recorded as what it is, and a separate verdict decides
  whether it can be retargeted onto a destination at all.
- Sampling density is reported, not assumed. A caller can see how many samples
  per second actually came back rather than trusting the requested rate.
"""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.models.video_extraction import GeminiUsage


class MotionSubjectKind(StrEnum):
    """What the analysed movement is performed by."""

    HUMAN_BODY = "human_body"
    ROBOT_ARM = "robot_arm"
    ROBOT_MOBILE = "robot_mobile"
    OTHER = "other"
    UNCLEAR = "unclear"


class JointVisibility(StrEnum):
    """How well one joint could be seen when a sample was taken."""

    CLEAR = "clear"
    PARTIAL = "partial"
    OCCLUDED = "occluded"


class ObservedMotionPhase(BaseModel):
    """One named span of the movement, such as a gait phase."""

    name: str = Field(
        description="Short phase name, for example 'right heel strike'.",
    )
    start_seconds: float = Field(
        description="Phase start in seconds from the beginning of the video.",
    )
    end_seconds: float = Field(
        description="Phase end in seconds from the beginning of the video.",
    )
    description: str = Field(
        description="What the body does during this phase, in one sentence.",
    )


class ObservedJointAngle(BaseModel):
    """One estimated joint angle at one instant of the video."""

    timestamp_seconds: float = Field(ge=0)
    joint_name: str = Field(min_length=1, max_length=60)
    side: Literal["left", "right", "center"]
    angle_degrees: float
    confidence: float = Field(ge=0, le=1)
    visibility: JointVisibility


class ProviderJointSample(BaseModel):
    """One joint reading in the compact shape the provider is asked for.

    Field names are single letters on purpose. A dense analysis returns
    hundreds of these, and the response is bounded by output tokens, not by
    frame rate: shortening the keys is what buys the extra frames.
    """

    t: float = Field(description="Seconds from the beginning of the video.")
    j: str = Field(
        description=(
            "Joint identity as side.name in lowercase English, for example "
            "'left.knee', 'right.hip', 'center.pelvis'."
        ),
    )
    a: float = Field(
        description=(
            "Joint angle in degrees; 0 is the neutral standing pose and "
            "flexion is positive."
        ),
    )
    c: float = Field(description="Confidence in this estimate, 0.0 to 1.0.")
    v: str = Field(description="Visibility: 'clear', 'partial', or 'occluded'.")


class ObservedMotionReport(BaseModel):
    """The provider-facing schema for one motion-analysis call.

    Kept flat and free of defaults so the structured-output schema stays
    simple, and free of any field derivable from the samples so the provider
    cannot contradict itself. The validated internal record is built from this
    by the service.
    """

    subject_kind: str = Field(
        description=(
            "One of 'human_body', 'robot_arm', 'robot_mobile', 'other', or "
            "'unclear'."
        ),
    )
    kinematic_chain: str = Field(
        description=(
            "The moving chain being observed, for example "
            "'bipedal_lower_limb' or 'serial_arm_6dof'."
        ),
    )
    phases: list[ObservedMotionPhase] = Field(
        description="Ordered phases of the movement.",
    )
    samples: list[ProviderJointSample] = Field(
        description=(
            "Timestamped joint-angle readings ordered by time. Report only "
            "joints actually visible; never fill a gap with a guess."
        ),
    )
    uncertainties: list[str] = Field(
        description=(
            "What could not be measured reliably: occlusion, camera angle, "
            "clothing, frame rate, or missing joints."
        ),
    )


class MotionEvidenceVerdict(StrEnum):
    """How far returned samples are from being observations at all."""

    USABLE = "usable"
    SUSPECT = "suspect"
    NOT_EVIDENCE = "not_evidence"


class MotionAuditCode(StrEnum):
    """Why the audit distrusted a set of samples."""

    NO_SAMPLES = "no_samples"
    MIRRORED_SIDES = "mirrored_sides"
    UNIFORM_CONFIDENCE = "uniform_confidence"
    UNIFORM_VISIBILITY = "uniform_visibility"
    ACYCLIC_ALL = "acyclic_all"
    ACYCLIC_SOME = "acyclic_some"


class MotionAuditFinding(BaseModel):
    """One reason to distrust the samples, in a form any language can render.

    `message` is the English sentence kept for logs and API consumers. `code`
    and `values` carry the same statement as data, so an interface can say it
    in the reader's own language without the server guessing which that is.
    """

    code: MotionAuditCode
    message: str = Field(min_length=1, max_length=500)
    values: dict[str, str] = Field(default_factory=dict)


class MotionEvidenceAudit(BaseModel):
    """What arithmetic alone can say about whether samples were measured.

    Every field is a count a reader can recompute from the samples. The audit
    never asks a model whether a model was honest.
    """

    verdict: MotionEvidenceVerdict
    findings: list[MotionAuditFinding] = Field(default_factory=list, max_length=12)
    mirrored_frame_ratio: float = Field(ge=0, le=1)
    distinct_confidence_values: int = Field(ge=0)
    distinct_visibility_values: int = Field(ge=0)
    acyclic_joints: list[str] = Field(default_factory=list, max_length=40)
    checked_joint_count: int = Field(ge=0)

    @property
    def is_usable(self) -> bool:
        """Report whether these samples may be treated as observations."""
        return self.verdict is MotionEvidenceVerdict.USABLE


class MotionRetargetVerdict(BaseModel):
    """Whether observed movement could drive one destination robot.

    A verdict is never an approval to move anything. It reports whether the
    observed kinematic chain has a defined correspondence in the destination,
    and names the evidence still missing when it does not.
    """

    retarget_supported: bool
    destination_robot_model: str | None = Field(default=None, max_length=160)
    observed_chain: str = Field(max_length=120)
    reason: str = Field(min_length=1, max_length=600)
    missing_evidence: list[str] = Field(default_factory=list, max_length=12)
    approved_for_execution: Literal[False] = False


class MotionAnalysisRecord(BaseModel):
    """One retained higher-frame-rate analysis of an approved source."""

    analysis_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    extraction_id: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    source_approved: Literal[True] = True

    requested_fps: float = Field(gt=0, le=24)
    window_start_seconds: float = Field(ge=0)
    window_end_seconds: float = Field(gt=0)
    media_resolution: Literal["medium"] = "medium"
    output_language: Literal["es", "en"] = "en"

    measurement_method: Literal["vision_model_estimate"] = "vision_model_estimate"
    physically_measured: Literal[False] = False
    subject_kind: MotionSubjectKind
    kinematic_chain: str = Field(max_length=120)
    joint_names: list[str] = Field(default_factory=list, max_length=40)
    phases: list[ObservedMotionPhase] = Field(default_factory=list, max_length=60)
    samples: list[ObservedJointAngle] = Field(default_factory=list, max_length=2000)
    uncertainties: list[str] = Field(default_factory=list, max_length=30)

    sample_count: int = Field(ge=0)
    distinct_joint_count: int = Field(ge=0)
    observed_span_seconds: float = Field(ge=0)
    samples_per_second: float = Field(ge=0)
    mean_confidence: float = Field(ge=0, le=1)
    clear_sample_count: int = Field(ge=0)

    audit: MotionEvidenceAudit
    retarget: MotionRetargetVerdict

    provider: Literal["vertex_ai", "gemini_api"]
    requested_model: str = Field(min_length=1)
    model_version: str | None = None
    elapsed_seconds: float = Field(ge=0)
    usage: GeminiUsage = Field(default_factory=GeminiUsage)
    cloud_calls_made: int = Field(default=1, ge=0, le=1)
    raw_response_retained: Literal[False] = False
    created_at: datetime


class MotionAnalysisRequest(BaseModel):
    """A caller's explicit instruction to spend one cloud call on movement."""

    frames_per_second: float = Field(default=4.0, gt=0, le=24)
    window_start_seconds: float = Field(default=0.0, ge=0, le=3600)
    window_seconds: float = Field(default=12.0, gt=0, le=120)
    output_language: Literal["es", "en"] = "es"
    acknowledge_cloud_cost: Literal[True]


class MotionAnalysisCall(BaseModel):
    """What one provider motion call returned, before it is interpreted."""

    report: ObservedMotionReport
    provider: Literal["vertex_ai", "gemini_api"]
    requested_model: str = Field(min_length=1)
    model_version: str | None = None
    elapsed_seconds: float = Field(ge=0)
    usage: GeminiUsage = Field(default_factory=GeminiUsage)
    cloud_calls_made: Literal[1] = 1
    raw_response_retained: Literal[False] = False
