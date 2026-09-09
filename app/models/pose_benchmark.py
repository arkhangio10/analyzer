"""Contracts for checking measured landmarks against ones a person placed.

A pose model that survives the plausibility audits has been shown not to be
fabricating. It has not been shown to be *right*. The only thing that shows
that is a person looking at frames of a real video, marking where the joints
actually are, and the system reporting how far its own answer sits from those
marks.

Two rules keep this from becoming self-grading:

- `authored_by` is `Literal["person"]`. A case a model labelled is not ground
  truth for a model, so the type refuses to hold one at all rather than
  carrying a flag somebody might forget to read.
- `source_sha256` binds labels to the exact bytes they were drawn on. Labels
  are positions in one particular video, and letting them float onto a
  different file would silently compare a measurement to marks made somewhere
  else.

The result of a comparison fails closed. No labels for this video means
`counts_as_external_validation` is false and the verdict is `unvalidated`,
which is not a passing grade and is never reported as one.
"""

from typing import Literal

from pydantic import BaseModel, Field


PoseBenchmarkVerdict = Literal["passed", "failed", "unvalidated"]


class LabelledLandmark(BaseModel):
    """Where a person says one joint actually is, in image coordinates."""

    name: str = Field(min_length=1, max_length=40)
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)


class LabelledPoseFrame(BaseModel):
    """One frame of a real video, labelled by hand."""

    timestamp_seconds: float = Field(ge=0)
    landmarks: list[LabelledLandmark] = Field(min_length=1, max_length=40)


class PoseBenchmarkCase(BaseModel):
    """One human-labelled video, and how close a measurement has to come."""

    case_id: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    authored_by: Literal["person"]
    labelled_by: str = Field(min_length=1, max_length=120)
    source_sha256: str = Field(min_length=64, max_length=64)
    source_description: str = Field(min_length=1, max_length=500)

    tolerance_normalised: float = Field(
        default=0.05,
        gt=0,
        le=0.5,
        description=(
            "How far a landmark may sit from its label, as a fraction of the "
            "image's diagonal, before that landmark counts as missed."
        ),
    )
    timestamp_tolerance_seconds: float = Field(default=0.05, gt=0, le=1.0)
    minimum_landmark_pass_ratio: float = Field(default=0.8, gt=0, le=1.0)

    frames: list[LabelledPoseFrame] = Field(min_length=1, max_length=200)


class LandmarkComparison(BaseModel):
    """How far one measured landmark sat from the label for it."""

    name: str = Field(min_length=1, max_length=40)
    timestamp_seconds: float = Field(ge=0)
    error_normalised: float = Field(ge=0)
    within_tolerance: bool


class PoseBenchmarkResult(BaseModel):
    """What comparing one measurement against one labelled case showed."""

    case_id: str | None = None
    verdict: PoseBenchmarkVerdict
    reason: str = Field(min_length=1, max_length=600)

    labelled_frame_count: int = Field(default=0, ge=0)
    compared_frame_count: int = Field(default=0, ge=0)
    compared_landmark_count: int = Field(default=0, ge=0)
    within_tolerance_count: int = Field(default=0, ge=0)
    landmark_pass_ratio: float = Field(default=0.0, ge=0, le=1)

    mean_error_normalised: float = Field(default=0.0, ge=0)
    worst_error_normalised: float = Field(default=0.0, ge=0)
    worst_landmark: str | None = Field(default=None, max_length=40)

    unmatched_labelled_frames: int = Field(default=0, ge=0)
    missing_landmarks: list[str] = Field(default_factory=list, max_length=40)
    comparisons: list[LandmarkComparison] = Field(default_factory=list, max_length=4000)

    counts_as_external_validation: bool = False
    approved_for_execution: Literal[False] = False

    @property
    def passed(self) -> bool:
        """Report a pass only when a person's labels were actually matched."""
        return self.verdict == "passed" and self.counts_as_external_validation
