"""Tests for the QC pipeline, and for the ADK behaviour that shaped it.

The pipeline's whole claim is that it checks stored metadata against stored
observations without spending anything and without stepping past a human
review. Each of those is asserted here rather than described:

- no stage may reach the provider, enforced by a service double that fails the
  test if it is called at all;
- every stage declaring `requires_approval` must do nothing without approval,
  asserted by walking the pipeline rather than by naming stages one at a time,
  so a stage added later is covered the day it is added;
- the pipeline must stop at the gate, not merely mark itself blocked.

The first test pins a fact about ADK, not about this code: `escalate` does not
stop a `SequentialAgent`. That is why the composition is written by hand. If a
future ADK makes it true, this test fails and the docstring explaining the
choice can be revisited -- which is the point of pinning it.
"""

from __future__ import annotations

import asyncio
import warnings
from datetime import datetime, timezone
from typing import AsyncGenerator
from uuid import uuid4

import pytest

from app.agents.qc_pipeline import (
    PipelineDeps,
    QcPipeline,
    STATE_APPROVED,
    STATE_EXTRACTION_ID,
    STATE_PROJECT_ID,
    run_qc_pipeline,
)
from app.models.motion_analysis import (
    MotionAnalysisRecord,
    MotionEvidenceVerdict,
    MotionRetargetVerdict,
    MotionSubjectKind,
    ObservedJointAngle,
)
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)
from app.models.qc_pipeline import StageOutcome
from app.services.motion_analysis_service import MotionAnalysisNotFoundError
from app.services.motion_evidence_audit import audit_motion_samples
from tests.unit.test_motion_evidence_audit import drawn_curve, walking_like


PROJECT_ID = "prj_qc000001"
EXTRACTION_ID = "vpr_qc000001"
WINDOW_SECONDS = 12.0


# --- the ADK fact that shaped the composition ------------------------------


def test_escalate_does_not_stop_a_sequential_agent() -> None:
    """Pinned because the approval gate would silently leak if it did not."""
    from google.adk.agents import BaseAgent
    from google.adk.events import Event, EventActions
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    ran: list[str] = []

    class Step(BaseAgent):
        async def _run_async_impl(self, ctx) -> AsyncGenerator[Event, None]:
            ran.append(self.name)
            yield Event(
                author=self.name,
                actions=EventActions(escalate=self.name == "gate"),
            )

    async def go() -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from google.adk.agents import SequentialAgent

            pipeline = SequentialAgent(
                name="p",
                sub_agents=[Step(name="first"), Step(name="gate"), Step(name="after")],
            )
        runner = InMemoryRunner(agent=pipeline, app_name="pin")
        session = await runner.session_service.create_session(
            app_name="pin", user_id="u"
        )
        async for _ in runner.run_async(
            user_id="u",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text="go")]),
        ):
            pass

    asyncio.run(go())

    assert ran == ["first", "gate", "after"], (
        "ADK now stops a SequentialAgent on escalate. The hand-written "
        "composition in app/agents/qc_pipeline.py can be reconsidered."
    )


# --- doubles ---------------------------------------------------------------


class FakeProcedureService:
    def __init__(self, record: ProjectVideoProcedureRecord | None) -> None:
        self._record = record

    def get(self, project_id: str, extraction_id: str) -> ProjectVideoProcedureRecord:
        if self._record is None:
            raise LookupError(extraction_id)
        return self._record


class FakeMotionService:
    """Stands in for the real service and fails loudly if asked to spend."""

    def __init__(self, analysis: MotionAnalysisRecord | None) -> None:
        self._analysis = analysis

    def latest_for_extraction(self, extraction_id: str) -> MotionAnalysisRecord:
        if self._analysis is None:
            raise MotionAnalysisNotFoundError(extraction_id)
        return self._analysis

    async def analyze(self, *args, **kwargs):
        raise AssertionError("The QC pipeline must never commission a cloud call.")


class FakeProjectService:
    def get(self, project_id: str) -> object:
        return object()


def extraction(
    status: ProjectVideoProcedureStatus = ProjectVideoProcedureStatus.APPROVED,
) -> ProjectVideoProcedureRecord:
    return ProjectVideoProcedureRecord(
        extraction_id=EXTRACTION_ID,
        project_id=PROJECT_ID,
        source_url="https://youtu.be/-fD2TSL2s7I",
        status=status,
        provider="vertex_ai",
        requested_model="gemini-2.5-flash-lite",
        cloud_calls_made=1,
        created_at=datetime.now(timezone.utc),
    )


def analysis(
    samples: list[ObservedJointAngle] | None = None,
    claimed: MotionEvidenceVerdict | None = None,
) -> MotionAnalysisRecord:
    """One stored analysis, optionally claiming a verdict its samples deny."""
    samples = samples if samples is not None else drawn_curve()
    audit = audit_motion_samples(samples, window_seconds=WINDOW_SECONDS)
    if claimed is not None:
        audit = audit.model_copy(update={"verdict": claimed})
    return MotionAnalysisRecord(
        analysis_id=f"mot_{uuid4().hex[:12]}",
        project_id=PROJECT_ID,
        extraction_id=EXTRACTION_ID,
        source_url="https://youtu.be/-fD2TSL2s7I",
        requested_fps=4.0,
        window_start_seconds=60.0,
        window_end_seconds=60.0 + WINDOW_SECONDS,
        subject_kind=MotionSubjectKind.HUMAN_BODY,
        kinematic_chain="bipedal_lower_limb",
        joint_names=sorted({item.joint_name for item in samples}),
        samples=samples,
        sample_count=len(samples),
        distinct_joint_count=len({f"{s.side}.{s.joint_name}" for s in samples}),
        observed_span_seconds=WINDOW_SECONDS,
        samples_per_second=len(samples) / WINDOW_SECONDS,
        mean_confidence=sum(s.confidence for s in samples) / len(samples),
        clear_sample_count=sum(1 for s in samples if s.visibility.value == "clear"),
        audit=audit,
        retarget=MotionRetargetVerdict(
            retarget_supported=False,
            observed_chain="bipedal_lower_limb",
            reason="Test record.",
        ),
        provider="vertex_ai",
        requested_model="gemini-2.5-flash-lite",
        elapsed_seconds=1.0,
        created_at=datetime.now(timezone.utc),
    )


def deps_for(
    status: ProjectVideoProcedureStatus = ProjectVideoProcedureStatus.APPROVED,
    stored: MotionAnalysisRecord | None = None,
) -> PipelineDeps:
    return PipelineDeps(
        project_service=FakeProjectService(),
        procedure_service=FakeProcedureService(extraction(status)),
        motion_service=FakeMotionService(stored),
    )


def run(deps: PipelineDeps):
    return asyncio.run(run_qc_pipeline(deps, PROJECT_ID, EXTRACTION_ID))


def outcomes(report) -> dict[str, StageOutcome]:
    return {stage.stage: stage.outcome for stage in report.stages}


# --- the gate --------------------------------------------------------------


def test_the_pipeline_stops_at_the_gate_when_nobody_approved() -> None:
    report = run(deps_for(ProjectVideoProcedureStatus.AWAITING_REVIEW, analysis()))

    assert report.approved is False
    assert report.proven is False
    assert report.blocked is True
    assert outcomes(report)["approval_gate"] is (
        StageOutcome.BLOCKED_AWAITING_APPROVAL
    )
    assert "motion" not in outcomes(report), "a stage past the gate ran anyway"
    assert "audit" not in outcomes(report)
    assert report.recomputed_verdict is None


def test_a_rejected_extraction_is_also_stopped() -> None:
    report = run(deps_for(ProjectVideoProcedureStatus.REJECTED, analysis()))

    assert report.approved is False
    assert "audit" not in outcomes(report)


def test_every_gated_stage_refuses_to_work_without_approval() -> None:
    """Walk the pipeline, so a stage added later is covered the day it lands."""
    deps = deps_for(ProjectVideoProcedureStatus.AWAITING_REVIEW, analysis())
    gated = [stage for stage in QcPipeline(deps).stages if stage.requires_approval]

    assert gated, "no stage requires approval; the gate would be decorative"

    for stage in gated:
        report = asyncio.run(_run_one(stage, approved=False))
        assert report is StageOutcome.BLOCKED_AWAITING_APPROVAL, stage.name


async def _run_one(stage, approved: bool) -> StageOutcome:
    """Run one stage alone against a session it did not populate."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    runner = InMemoryRunner(agent=stage, app_name="one")
    session = await runner.session_service.create_session(
        app_name="one",
        user_id="u",
        state={
            STATE_PROJECT_ID: PROJECT_ID,
            STATE_EXTRACTION_ID: EXTRACTION_ID,
            STATE_APPROVED: approved,
        },
    )
    async for _ in runner.run_async(
        user_id="u",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text="go")]),
    ):
        pass
    finished = await runner.session_service.get_session(
        app_name="one", user_id="u", session_id=session.id
    )
    return StageOutcome(finished.state[f"qc.stage.{stage.name}"]["outcome"])


# --- what it proves, and what it does not ----------------------------------


def test_metadata_that_survives_recomputation_is_reported_as_observed() -> None:
    report = run(deps_for(stored=analysis(walking_like())))

    assert report.approved is True
    assert report.proven is True
    assert report.claimed_verdict == report.recomputed_verdict
    assert outcomes(report)["audit"] is StageOutcome.COMPLETED
    assert outcomes(report)["report"] is StageOutcome.COMPLETED


def test_metadata_its_own_samples_deny_is_not_reported_as_observed() -> None:
    stored = analysis(drawn_curve(), claimed=MotionEvidenceVerdict.USABLE)

    report = run(deps_for(stored=stored))

    assert report.claimed_verdict == "usable"
    assert report.recomputed_verdict == MotionEvidenceVerdict.NOT_EVIDENCE.value
    assert report.proven is False
    assert outcomes(report)["audit"] is StageOutcome.FAILED


def test_approval_alone_proves_nothing_without_stored_samples() -> None:
    report = run(deps_for(stored=None))

    assert report.approved is True
    assert report.proven is False
    assert outcomes(report)["motion"] is StageOutcome.NO_EVIDENCE
    assert outcomes(report)["audit"] is StageOutcome.NO_EVIDENCE
    assert report.analysis_id is None


def test_a_failed_extraction_has_no_claims_to_check() -> None:
    report = run(deps_for(ProjectVideoProcedureStatus.EXTRACTION_FAILED, analysis()))

    assert outcomes(report)["extraction"] is StageOutcome.FAILED
    assert report.proven is False


# --- cost ------------------------------------------------------------------


def test_a_whole_run_spends_nothing() -> None:
    report = run(deps_for(stored=analysis(walking_like())))

    assert report.cloud_calls_made == 0
    assert all(stage.cloud_calls_made == 0 for stage in report.stages)


def test_the_run_records_what_it_was_about() -> None:
    report = run(deps_for(stored=analysis(walking_like())))

    assert report.project_id == PROJECT_ID
    assert report.extraction_id == EXTRACTION_ID
    assert report.source_url == "https://youtu.be/-fD2TSL2s7I"
    assert report.analysis_id is not None
    assert [stage.stage for stage in report.stages] == [
        "ingest",
        "extraction",
        "approval_gate",
        "motion",
        "audit",
        "report",
    ]
