"""The QC pipeline as ADK agents, composed so the approval gate cannot leak.

Each stage is a real `google.adk` agent, run through a real ADK runner, passing
real session state between stages. What the stages do is deterministic: they
read records the services already produced and recompute the audit over stored
samples. No stage initiates a provider call, so running the pipeline costs
nothing and cannot quietly spend a cloud call on a person's behalf.

## Why the composition is written here rather than taken from ADK

ADK ships `SequentialAgent`, and it very nearly fits. It does not, for one
measured reason: a sub-agent that sets `escalate` does **not** stop a
`SequentialAgent`. Every later sub-agent still runs. `LoopAgent` is what
`escalate` terminates. A gate built on it would look like it stopped the
pipeline and would not, which is the worst failure available here -- a
governance guarantee that reads as enforced and is not.

So `QcPipeline` runs its stages itself and stops at the first blocked one. That
is a dozen lines, and it puts the stopping rule where it can be read and tested
instead of inheriting it from a class whose semantics point elsewhere.
`tests/unit/test_qc_pipeline.py` pins the ADK behaviour that forced this, so a
future version changing it will say so out loud.

## Why the gate is checked in the base class

`PipelineStage` checks `requires_approval` before it calls `_perform`, so a
stage added later inherits the check by existing rather than by remembering.
A test walks every stage in the pipeline and asserts each one that requires
approval does no work without it, so the enforcement cannot be quietly dropped
from a single stage.

This is the pipeline's second line, not its first. `MotionAnalysisService`
already refuses to analyse an unapproved procedure at the point where the cloud
call would be spent, and that check is the load-bearing one, because it guards
the money and it holds whether or not anybody runs this pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, ClassVar

from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.adk.runners import InMemoryRunner
from google.genai import types

from app.models.project_video_procedure import ProjectVideoProcedureStatus
from app.models.qc_pipeline import QcReport, StageOutcome, StageReport
from app.services.motion_evidence_audit import audit_motion_samples


logger = logging.getLogger(__name__)

STATE_PROJECT_ID = "qc.project_id"
STATE_EXTRACTION_ID = "qc.extraction_id"
STATE_SOURCE_URL = "qc.source_url"
STATE_APPROVED = "qc.approved"
STATE_ANALYSIS_ID = "qc.analysis_id"
STATE_CLAIMED_VERDICT = "qc.claimed_verdict"
STATE_RECOMPUTED_VERDICT = "qc.recomputed_verdict"
STATE_SQL_VERDICT = "qc.sql_verdict"
STATE_PROVEN = "qc.proven"


@dataclass
class PipelineDeps:
    """The services the stages read. None of them is asked to spend money."""

    project_service: Any
    procedure_service: Any
    motion_service: Any
    evidence_store: Any | None = None


class PipelineStage(BaseAgent):
    """One stage, gated before it can do anything."""

    requires_approval: ClassVar[bool] = False

    def __init__(self, name: str, deps: PipelineDeps) -> None:
        super().__init__(name=name)
        # BaseAgent is a pydantic model; dependencies are not part of its schema.
        object.__setattr__(self, "_deps", deps)

    @property
    def deps(self) -> PipelineDeps:
        """Return the services this stage reads."""
        return self._deps

    async def _run_async_impl(
        self,
        ctx: Any,
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        if self.requires_approval and not state.get(STATE_APPROVED):
            yield self._event(
                StageReport(
                    stage=self.name,
                    outcome=StageOutcome.BLOCKED_AWAITING_APPROVAL,
                    detail=(
                        "Nobody has approved this extraction, so nothing "
                        "downstream of the review ran."
                    ),
                ),
                {},
            )
            return

        try:
            report, delta = await self._perform(state)
        except Exception as error:  # noqa: BLE001 - a stage failing is a result
            logger.warning("Stage %s failed: %s", self.name, error)
            report, delta = (
                StageReport(
                    stage=self.name,
                    outcome=StageOutcome.FAILED,
                    detail=f"{type(error).__name__}: {error}"[:400],
                ),
                {},
            )
        yield self._event(report, delta)

    def _event(self, report: StageReport, delta: dict[str, Any]) -> Event:
        return Event(
            author=self.name,
            actions=EventActions(state_delta={**delta, f"qc.stage.{self.name}": report.model_dump(mode="json")}),
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"{report.outcome.value}: {report.detail}")],
            ),
        )

    async def _perform(
        self,
        state: Any,
    ) -> tuple[StageReport, dict[str, Any]]:
        """Do this stage's work; return what happened and what to record."""
        raise NotImplementedError


class IngestStage(PipelineStage):
    """Confirm the project and the extraction this run is about exist."""

    def __init__(self, deps: PipelineDeps) -> None:
        super().__init__("ingest", deps)

    async def _perform(self, state: Any) -> tuple[StageReport, dict[str, Any]]:
        project_id = state.get(STATE_PROJECT_ID)
        extraction_id = state.get(STATE_EXTRACTION_ID)
        record = self.deps.procedure_service.get(project_id, extraction_id)
        return (
            StageReport(
                stage=self.name,
                outcome=StageOutcome.COMPLETED,
                detail=f"Extraction {extraction_id} belongs to {project_id}.",
            ),
            {STATE_SOURCE_URL: record.source_url},
        )


class ExtractionStage(PipelineStage):
    """Report where the claimed metadata came from, without producing more."""

    def __init__(self, deps: PipelineDeps) -> None:
        super().__init__("extraction", deps)

    async def _perform(self, state: Any) -> tuple[StageReport, dict[str, Any]]:
        record = self.deps.procedure_service.get(
            state.get(STATE_PROJECT_ID), state.get(STATE_EXTRACTION_ID)
        )
        if record.status is ProjectVideoProcedureStatus.EXTRACTION_FAILED:
            return (
                StageReport(
                    stage=self.name,
                    outcome=StageOutcome.FAILED,
                    detail=(
                        f"Extraction failed: {record.failure_code or 'unknown'}. "
                        "There are no claims to check."
                    ),
                ),
                {},
            )
        provider = record.provider or "none"
        model = record.model_version or record.requested_model or "unknown"
        return (
            StageReport(
                stage=self.name,
                outcome=StageOutcome.COMPLETED,
                detail=(
                    f"Claims came from {provider} ({model}) at a cost of "
                    f"{record.cloud_calls_made} cloud call(s). This stage spent none."
                ),
                cloud_calls_made=0,
            ),
            {},
        )


class ApprovalGateStage(PipelineStage):
    """Record whether a person approved this extraction. Nothing else."""

    def __init__(self, deps: PipelineDeps) -> None:
        super().__init__("approval_gate", deps)

    async def _perform(self, state: Any) -> tuple[StageReport, dict[str, Any]]:
        record = self.deps.procedure_service.get(
            state.get(STATE_PROJECT_ID), state.get(STATE_EXTRACTION_ID)
        )
        approved = record.status is ProjectVideoProcedureStatus.APPROVED
        if not approved:
            return (
                StageReport(
                    stage=self.name,
                    outcome=StageOutcome.BLOCKED_AWAITING_APPROVAL,
                    detail=(
                        f"The extraction is {record.status.value}, not approved, "
                        "so the pipeline stops here."
                    ),
                ),
                {STATE_APPROVED: False},
            )
        return (
            StageReport(
                stage=self.name,
                outcome=StageOutcome.COMPLETED,
                detail="A person approved this extraction; checking may proceed.",
            ),
            {STATE_APPROVED: True},
        )


class MotionStage(PipelineStage):
    """Find the stored observations, without commissioning new ones."""

    requires_approval: ClassVar[bool] = True

    def __init__(self, deps: PipelineDeps) -> None:
        super().__init__("motion", deps)

    async def _perform(self, state: Any) -> tuple[StageReport, dict[str, Any]]:
        extraction_id = state.get(STATE_EXTRACTION_ID)
        try:
            analysis = self.deps.motion_service.latest_for_extraction(extraction_id)
        except LookupError:
            return (
                StageReport(
                    stage=self.name,
                    outcome=StageOutcome.NO_EVIDENCE,
                    detail=(
                        "No motion analysis is stored for this extraction. "
                        "Sampling one costs a cloud call, which this pipeline "
                        "does not spend."
                    ),
                ),
                {},
            )
        return (
            StageReport(
                stage=self.name,
                outcome=StageOutcome.COMPLETED,
                detail=(
                    f"{analysis.sample_count} stored samples across "
                    f"{analysis.distinct_joint_count} joints."
                ),
            ),
            {
                STATE_ANALYSIS_ID: analysis.analysis_id,
                STATE_CLAIMED_VERDICT: analysis.audit.verdict.value,
            },
        )


class AuditStage(PipelineStage):
    """Recompute the verdict from the stored samples and compare it."""

    requires_approval: ClassVar[bool] = True

    def __init__(self, deps: PipelineDeps) -> None:
        super().__init__("audit", deps)

    async def _perform(self, state: Any) -> tuple[StageReport, dict[str, Any]]:
        analysis_id = state.get(STATE_ANALYSIS_ID)
        if not analysis_id:
            return (
                StageReport(
                    stage=self.name,
                    outcome=StageOutcome.NO_EVIDENCE,
                    detail="There are no stored samples to recompute a verdict from.",
                ),
                {},
            )
        analysis = self.deps.motion_service.latest_for_extraction(
            state.get(STATE_EXTRACTION_ID)
        )
        window = analysis.window_end_seconds - analysis.window_start_seconds
        recomputed = audit_motion_samples(analysis.samples, window_seconds=window)
        claimed = analysis.audit.verdict
        agrees = recomputed.verdict is claimed

        delta: dict[str, Any] = {
            STATE_RECOMPUTED_VERDICT: recomputed.verdict.value,
            STATE_PROVEN: agrees,
        }
        detail = (
            f"Recomputed {recomputed.verdict.value} from {len(analysis.samples)} "
            f"stored samples; the record claims {claimed.value}."
        )

        sql = self._sql_verdict(analysis_id, window)
        if sql is not None:
            delta[STATE_SQL_VERDICT] = sql
            detail += f" ClickHouse independently reached {sql}."

        return (
            StageReport(
                stage=self.name,
                outcome=StageOutcome.COMPLETED if agrees else StageOutcome.FAILED,
                detail=detail[:400],
            ),
            delta,
        )

    def _sql_verdict(self, analysis_id: str, window: float) -> str | None:
        store = self.deps.evidence_store
        if store is None or not store.is_available:
            return None
        audit = store.audit_from_sql(analysis_id, window_seconds=window)
        return audit.verdict.value if audit is not None else None


class ReportStage(PipelineStage):
    """Say what was established, in the narrowest terms that stay true."""

    requires_approval: ClassVar[bool] = True

    def __init__(self, deps: PipelineDeps) -> None:
        super().__init__("report", deps)

    async def _perform(self, state: Any) -> tuple[StageReport, dict[str, Any]]:
        if state.get(STATE_PROVEN):
            detail = (
                "The stored metadata was recomputed from the stored samples and "
                "matched, so it was observed rather than asserted."
            )
        elif state.get(STATE_RECOMPUTED_VERDICT):
            detail = (
                "The recomputed verdict disagrees with the stored one, so the "
                "stored metadata is not supported by its own samples."
            )
        else:
            detail = (
                "Nothing was proven: there were no stored samples to recompute "
                "a verdict from."
            )
        return (
            StageReport(
                stage=self.name,
                outcome=StageOutcome.COMPLETED,
                detail=detail,
            ),
            {},
        )


class QcPipeline(BaseAgent):
    """Run the stages in order and stop at the first one that is blocked."""

    def __init__(self, deps: PipelineDeps, name: str = "qc_pipeline") -> None:
        super().__init__(name=name)
        stages: list[PipelineStage] = [
            IngestStage(deps),
            ExtractionStage(deps),
            ApprovalGateStage(deps),
            MotionStage(deps),
            AuditStage(deps),
            ReportStage(deps),
        ]
        object.__setattr__(self, "_stages", stages)

    @property
    def stages(self) -> list[PipelineStage]:
        """Return the stages in the order they run."""
        return self._stages

    async def _run_async_impl(self, ctx: Any) -> AsyncGenerator[Event, None]:
        for stage in self._stages:
            blocked = False
            async for event in stage.run_async(ctx):
                yield event
                blocked = blocked or self._is_blocked(event)
            if blocked:
                return

    @staticmethod
    def _is_blocked(event: Event) -> bool:
        delta = (event.actions.state_delta or {}) if event.actions else {}
        for key, value in delta.items():
            if key.startswith("qc.stage.") and isinstance(value, dict):
                if value.get("outcome") == StageOutcome.BLOCKED_AWAITING_APPROVAL.value:
                    return True
        return False


def report_from_state(
    state: Any,
    project_id: str,
    extraction_id: str,
) -> QcReport:
    """Assemble the run's account from the session state it left behind."""
    stages = [
        StageReport.model_validate(value)
        for key, value in state.items()
        if key.startswith("qc.stage.") and isinstance(value, dict)
    ]
    order = {
        name: index
        for index, name in enumerate(
            ["ingest", "extraction", "approval_gate", "motion", "audit", "report"]
        )
    }
    stages.sort(key=lambda item: order.get(item.stage, len(order)))
    return QcReport(
        project_id=project_id,
        extraction_id=extraction_id,
        analysis_id=state.get(STATE_ANALYSIS_ID),
        source_url=state.get(STATE_SOURCE_URL),
        stages=stages,
        approved=bool(state.get(STATE_APPROVED)),
        proven=bool(state.get(STATE_PROVEN)),
        claimed_verdict=state.get(STATE_CLAIMED_VERDICT),
        recomputed_verdict=state.get(STATE_RECOMPUTED_VERDICT),
        sql_verdict=state.get(STATE_SQL_VERDICT),
        cloud_calls_made=0,
        created_at=datetime.now(timezone.utc),
    )


APP_NAME = "aprendiz_qc"


async def run_qc_pipeline(
    deps: PipelineDeps,
    project_id: str,
    extraction_id: str,
    user_id: str = "operator",
) -> QcReport:
    """Run one QC pass over one extraction and return what it established.

    The run is seeded with the two identifiers and nothing else, so every other
    value in the report was put there by a stage that did the work.
    """
    runner = InMemoryRunner(agent=QcPipeline(deps), app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        state={
            STATE_PROJECT_ID: project_id,
            STATE_EXTRACTION_ID: extraction_id,
        },
    )
    async for _ in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=f"Audit {extraction_id}.")],
        ),
    ):
        pass
    finished = await runner.session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session.id
    )
    return report_from_state(finished.state, project_id, extraction_id)
