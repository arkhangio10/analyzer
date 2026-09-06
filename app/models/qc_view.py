"""Contracts for the QC console's two views.

The console answers one question about a video library: which metadata was
actually observed, and which was only asserted. Both views are shaped so they
cannot answer it more confidently than the data allows.

The library view carries `evidence_available` because there are two different
reasons a library can look empty: nothing has been analysed, or the columnar
store that holds library-scale evidence is not reachable. Those mean opposite
things to a reader, so the view says which one applies and still lists what the
local record store holds, rather than showing an empty table that implies a
clean library.

The detail view carries the audit's counts, not just its verdict, because the
claim being made is that the verdict is recomputable. A reader who can see the
counts can check the arithmetic; a reader shown only a verdict is being asked
to trust one.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class QcVerdictCount(BaseModel):
    """How many of a project's analyses reached one verdict."""

    verdict: str = Field(min_length=1, max_length=40)
    analyses: int = Field(ge=0)
    samples: int = Field(ge=0)
    tokens: int = Field(ge=0)


class QcUntrustedAsset(BaseModel):
    """One analysis whose evidence did not survive the audit."""

    analysis_id: str = Field(min_length=1)
    source_url: str = ""
    verdict: str = Field(min_length=1, max_length=40)
    sample_count: int = Field(ge=0)
    codes: list[str] = Field(default_factory=list, max_length=20)


class QcAssetSummary(BaseModel):
    """One analysed asset, as the local record store knows it."""

    analysis_id: str = Field(min_length=1)
    extraction_id: str = Field(min_length=1)
    source_url: str = ""
    verdict: str = Field(min_length=1, max_length=40)
    sample_count: int = Field(ge=0)
    distinct_joint_count: int = Field(ge=0)
    created_at: datetime


class QcLibraryView(BaseModel):
    """What is known about one project's analysed video."""

    project_id: str = Field(min_length=1)
    evidence_available: bool
    evidence_note: str = Field(min_length=1, max_length=400)
    verdicts: list[QcVerdictCount] = Field(default_factory=list, max_length=20)
    untrusted: list[QcUntrustedAsset] = Field(default_factory=list, max_length=200)
    analyses: list[QcAssetSummary] = Field(default_factory=list, max_length=200)


class QcFindingView(BaseModel):
    """One audit finding, with the values it was reached from.

    `values` stays `dict[str, str]`, matching `MotionAuditFinding`. They are not
    all numbers -- a visibility reads `partial` -- and they are carried as data
    precisely so an interface can restate the finding in the reader's language.
    Coercing them to floats would discard the ones that say the most.
    """

    code: str = Field(min_length=1, max_length=60)
    message: str = Field(min_length=1, max_length=400)
    values: dict[str, str] = Field(default_factory=dict)


class QcSamplePoint(BaseModel):
    """One joint reading, small enough to send a whole series of them."""

    joint: str = Field(min_length=1, max_length=60)
    side: str = Field(max_length=20)
    t: float
    angle: float


class QcAssetDetail(BaseModel):
    """One analysis, with everything a reader needs to check its verdict."""

    analysis_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    extraction_id: str = Field(min_length=1)
    source_url: str = ""

    verdict: str = Field(min_length=1, max_length=40)
    physically_measured: bool = False
    measurement_method: str = Field(default="", max_length=60)

    sample_count: int = Field(ge=0)
    distinct_joint_count: int = Field(ge=0)
    observed_span_seconds: float = Field(ge=0)
    samples_per_second: float = Field(ge=0)
    mean_confidence: float = Field(ge=0)
    clear_sample_count: int = Field(ge=0)

    mirrored_frame_ratio: float = Field(ge=0)
    distinct_confidence_values: int = Field(ge=0)
    distinct_visibility_values: int = Field(ge=0)
    acyclic_joints: list[str] = Field(default_factory=list, max_length=60)
    checked_joint_count: int = Field(ge=0)
    findings: list[QcFindingView] = Field(default_factory=list, max_length=20)

    provider: str = Field(default="", max_length=40)
    model_version: str = Field(default="", max_length=120)
    cloud_calls_made: int = Field(ge=0)
    created_at: datetime

    series: list[QcSamplePoint] = Field(default_factory=list, max_length=4000)
