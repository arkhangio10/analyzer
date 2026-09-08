"""Contracts for the exported agent package.

The package is the product's final deliverable: a versioned, self-contained
Docker package that runs the agent and shows what it learned. What it can
truthfully claim is fixed here as typed guarantees rather than promised in
prose, in the same way `approved_for_execution` is permanently false on an
adaptation plan. A reader of `skill.json` can trust those fields without
trusting the person who wrote the README.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.adaptation import DestinationAdaptationPlan
from app.models.computer_practice import ComputerPractice
from app.models.motion_analysis import MotionAnalysisRecord, MotionRetargetVerdict
from app.models.project import DestinationContract, ExecutionDestination
from app.models.skill import Skill
from app.models.video_extraction import GeminiUsage


class AgentGuarantees(BaseModel):
    """What an exported agent is not, made permanent by the type system.

    Every field is `Literal[False]`, so a package whose skill claims otherwise
    fails validation rather than being served.
    """

    # The agent knows the procedure. It has never been authorised to run it.
    approved_for_execution: Literal[False] = False
    # Joint angles in the evidence are a vision model's estimate, not sensors.
    physically_measured: Literal[False] = False
    # Hardware stays behind a separate, safety-approved adapter.
    hardware_execution_approved: Literal[False] = False
    # Learning here is procedural-memory acquisition; no weights were changed.
    model_weights_updated: Literal[False] = False
    # The user's own video files never leave the machine they were kept on.
    uploads_included: Literal[False] = False
    # No credential, key, or `.env` content is inside the package or image.
    secrets_included: Literal[False] = False
    # Serving what was learned costs nothing; the agent needs no provider.
    provider_calls_at_runtime: Literal[False] = False


class ExtractionLineage(BaseModel):
    """Where the learned procedure came from, and what producing it cost."""

    source_url: str = Field(min_length=1)
    source_approved: Literal[True] = True
    provider: Literal["vertex_ai", "gemini_api"] | None = None
    requested_model: str | None = None
    model_version: str | None = None
    usage: GeminiUsage = Field(default_factory=GeminiUsage)
    elapsed_seconds: float | None = Field(default=None, ge=0)
    extracted_at: datetime
    reviewed_at: datetime | None = None
    review_notes: str | None = Field(default=None, max_length=2000)


class ExportedAgentSkill(BaseModel):
    """The whole of what one exported agent knows: `skill.json`.

    Built on the existing `Skill` contract rather than beside it, and carrying
    the destination-specific evidence an executor would need to decide what
    it may attempt. Nothing in here authorises execution.
    """

    schema_version: Literal[1] = 1
    language: Literal["es", "en"] = "es"
    skill: Skill
    project_id: str = Field(min_length=1)
    extraction_id: str = Field(min_length=1)
    procedure_version: int = Field(ge=1)
    destination: ExecutionDestination
    destination_contract: DestinationContract
    adaptation: DestinationAdaptationPlan | None = None
    motion_evidence: MotionAnalysisRecord | None = None
    retarget: MotionRetargetVerdict | None = None
    practices: list[ComputerPractice] = Field(default_factory=list, max_length=50)
    lineage: ExtractionLineage
    guarantees: AgentGuarantees = Field(default_factory=AgentGuarantees)
    exported_at: datetime


class PackageFile(BaseModel):
    """One file in the package and the digest that proves it is unchanged."""

    path: str = Field(min_length=1, max_length=300)
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class AgentPackageManifest(BaseModel):
    """What was packaged, from what, and how to run it: `manifest.json`.

    Retained per project so a package can be listed, inspected and rebuilt
    byte-for-byte later from the same records and the same `created_at`.
    """

    schema_version: Literal[1] = 1
    package_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    extraction_id: str = Field(min_length=1)
    procedure_version: int = Field(ge=1)
    destination: ExecutionDestination
    language: Literal["es", "en"] = "es"
    app_version: str = Field(min_length=1)
    base_image: str = Field(min_length=1)
    created_at: datetime
    directory_name: str = Field(min_length=1)
    files: list[PackageFile] = Field(default_factory=list)
    launcher: list[str] = Field(default_factory=list)
    health_endpoint: str = "/health"
    skill_endpoint: str = "/api/skill"
    frozen_case_count: int = Field(ge=0)
    guarantees: AgentGuarantees = Field(default_factory=AgentGuarantees)


class AgentPackageRequest(BaseModel):
    """What a caller may choose when asking for a package."""

    language: Literal["es", "en"] = "es"
