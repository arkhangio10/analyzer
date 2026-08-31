"""Higher-frame-rate motion analysis of an already approved source.

The procedure pass answers what is being taught. This pass answers how the
body actually moves, which is the only question whose answer can ever become a
trajectory. It costs one cloud call, so it runs on a source a person already
approved and reviewed, never on a source it chose itself.

Everything the provider returns is treated as an estimate under suspicion:
samples with no joint, no time, or an impossible confidence are dropped rather
than repaired, and every repair the service does make is written into the
record's uncertainties so a reader can see it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.models.motion_analysis import (
    JointVisibility,
    MotionAnalysisRecord,
    MotionAnalysisRequest,
    MotionSubjectKind,
    ObservedJointAngle,
    ObservedMotionPhase,
    ProviderJointSample,
)
from app.models.project import ProjectDraft
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)
from app.models.robot_profile import ARP1RobotProfile
from app.core.config import get_settings
from app.services.gemini_service import GeminiService
from app.services.motion_evidence_audit import audit_motion_samples
from app.services.motion_retarget import build_retarget_verdict
from app.services.record_store import JsonRecordStore


MAX_SAMPLES = 2000
MAX_PHASES = 60

# A dense analysis is bounded by output tokens, not by frame rate: the model
# runs out of room to write samples long before it runs out of frames to look
# at. These two constants turn that ceiling into a request the caller can be
# refused *before* being charged for a response that would arrive truncated.
TOKENS_PER_SAMPLE_ROW = 30
ASSUMED_JOINTS_PER_FRAME = 8
BUDGET_HEADROOM = 0.9
PROMPT_OVERHEAD_TOKENS = 400


class MotionAnalysisNotApprovedError(ValueError):
    """Raised when analysis is requested for a procedure nobody approved."""


class MotionAnalysisBudgetError(ValueError):
    """Raised when a request would be truncated, before any call is made."""


class MotionAnalysisNotFoundError(LookupError):
    """Raised when no retained analysis exists for an extraction."""


class MotionAnalysisService:
    """Turn one approved video into timestamped, inspectable joint evidence."""

    def __init__(
        self,
        gemini_service: GeminiService,
        store: JsonRecordStore | None = None,
        output_token_ceiling: int | None = None,
    ) -> None:
        self._gemini_service = gemini_service
        self._store = store
        self._output_token_ceiling = output_token_ceiling or (
            get_settings().google_genai_motion_max_output_tokens
        )
        self._records: dict[str, MotionAnalysisRecord] = (
            store.load_all(MotionAnalysisRecord) if store else {}
        )

    @property
    def is_durable(self) -> bool:
        """Report whether paid motion evidence survives a restart."""
        return bool(self._store and self._store.is_durable)

    def latest_for_extraction(self, extraction_id: str) -> MotionAnalysisRecord:
        """Return the newest retained analysis for one extraction."""
        matches = [
            record
            for record in self._records.values()
            if record.extraction_id == extraction_id
        ]
        if not matches:
            raise MotionAnalysisNotFoundError(extraction_id)
        return max(matches, key=lambda record: record.created_at)

    async def analyze(
        self,
        project: ProjectDraft,
        record: ProjectVideoProcedureRecord,
        request: MotionAnalysisRequest,
        profile: ARP1RobotProfile | None = None,
        joint_map: dict[str, str] | None = None,
    ) -> MotionAnalysisRecord:
        """Spend one cloud call sampling an approved video for movement."""
        if record.status is not ProjectVideoProcedureStatus.APPROVED:
            raise MotionAnalysisNotApprovedError(
                "Motion analysis costs a cloud call and runs only on a "
                "procedure a person has already approved."
            )

        self.check_budget(request)

        window_end = request.window_start_seconds + request.window_seconds
        call = await self._gemini_service.analyze_motion(
            video_url=record.source_url,
            frames_per_second=request.frames_per_second,
            window_start_seconds=request.window_start_seconds,
            window_end_seconds=window_end,
            output_language=request.output_language,
        )

        notes: list[str] = []
        samples = self._clean_samples(call.report.samples, notes)
        phases = self._clean_phases(call.report.phases, notes)
        subject_kind = self._read_subject_kind(call.report.subject_kind, notes)
        chain = (call.report.kinematic_chain or "unknown")[:120]
        stats = self._measure(samples)
        audit = audit_motion_samples(
            samples,
            window_seconds=request.window_seconds,
        )

        analysis = MotionAnalysisRecord(
            analysis_id=f"mot_{uuid4().hex[:12]}",
            project_id=project.project_id,
            extraction_id=record.extraction_id,
            source_url=record.source_url,
            requested_fps=request.frames_per_second,
            window_start_seconds=request.window_start_seconds,
            window_end_seconds=window_end,
            output_language=request.output_language,
            subject_kind=subject_kind,
            kinematic_chain=chain,
            joint_names=sorted({sample.joint_name for sample in samples})[:40],
            phases=phases,
            samples=samples,
            uncertainties=[
                item[:500]
                for item in (list(call.report.uncertainties) + notes)
            ][:30],
            audit=audit,
            retarget=build_retarget_verdict(
                project=project,
                subject_kind=subject_kind,
                kinematic_chain=chain,
                samples=samples,
                audit=audit,
                profile=profile,
                joint_map=joint_map,
                language=request.output_language,
            ),
            provider=call.provider,
            requested_model=call.requested_model,
            model_version=call.model_version,
            elapsed_seconds=call.elapsed_seconds,
            usage=call.usage,
            cloud_calls_made=call.cloud_calls_made,
            created_at=datetime.now(timezone.utc),
            **stats,
        )
        self._records[analysis.analysis_id] = analysis
        if self._store:
            self._store.save(analysis.analysis_id, analysis)
        return analysis

    def max_window_seconds(self, frames_per_second: float) -> float:
        """Return the longest window that can be answered without truncation."""
        budget = self._output_token_ceiling * BUDGET_HEADROOM
        rows = (budget - PROMPT_OVERHEAD_TOKENS) / TOKENS_PER_SAMPLE_ROW
        frames = rows / ASSUMED_JOINTS_PER_FRAME
        return max(round(frames / frames_per_second, 1), 0.0)

    def check_budget(self, request: MotionAnalysisRequest) -> None:
        """Refuse a request that could only come back truncated.

        Nobody should pay for a response that runs out of room halfway through
        the samples, so the arithmetic happens here rather than in the bill.
        """
        allowed = self.max_window_seconds(request.frames_per_second)
        if request.window_seconds <= allowed:
            return
        raise MotionAnalysisBudgetError(
            f"At {request.frames_per_second:g} fps this analysis can answer at "
            f"most {allowed:g} seconds of video before the response is cut "
            f"off, and {request.window_seconds:g} seconds were requested. "
            "Shorten the window or lower the frame rate; no call was made and "
            "nothing was billed."
        )

    @staticmethod
    def _read_subject_kind(value: str, notes: list[str]) -> MotionSubjectKind:
        try:
            return MotionSubjectKind((value or "").strip().casefold())
        except ValueError:
            notes.append(
                "The analysis did not name a recognised kind of moving "
                "subject, so it is recorded as unclear."
            )
            return MotionSubjectKind.UNCLEAR

    @staticmethod
    def _split_joint(identity: str) -> tuple[str, str]:
        """Split a compact 'left.knee' identity into a side and a joint name."""
        head, separator, tail = identity.strip().casefold().partition(".")
        if separator and head in {"left", "right", "center"}:
            return head, tail.strip()
        return "center", identity.strip().casefold()

    @staticmethod
    def _clean_samples(
        samples: list[ProviderJointSample],
        notes: list[str],
    ) -> list[ObservedJointAngle]:
        """Keep only samples that carry a joint, a time, and a real angle."""
        kept: list[ObservedJointAngle] = []
        dropped = 0
        clamped = 0
        unreadable_visibility = 0
        for sample in samples:
            side, joint = MotionAnalysisService._split_joint(sample.j)
            if not joint or sample.t < 0:
                dropped += 1
                continue
            confidence = sample.c
            if not 0.0 <= confidence <= 1.0:
                confidence = min(max(confidence, 0.0), 1.0)
                clamped += 1
            try:
                visibility = JointVisibility(sample.v.strip().casefold())
            except ValueError:
                visibility = JointVisibility.PARTIAL
                unreadable_visibility += 1
            kept.append(
                ObservedJointAngle(
                    timestamp_seconds=round(sample.t, 3),
                    joint_name=joint[:60],
                    side=side,
                    angle_degrees=round(sample.a, 2),
                    confidence=round(confidence, 3),
                    visibility=visibility,
                )
            )
        if dropped:
            notes.append(
                f"{dropped} sample(s) arrived without a joint name or with a "
                "negative timestamp and were discarded rather than repaired."
            )
        if clamped:
            notes.append(
                f"{clamped} sample(s) reported a confidence outside 0..1, "
                "which was clamped; treat those estimates with extra suspicion."
            )
        if unreadable_visibility:
            notes.append(
                f"{unreadable_visibility} sample(s) reported an unrecognised "
                "visibility and are counted as only partially visible."
            )
        kept.sort(
            key=lambda item: (
                item.timestamp_seconds,
                item.side,
                item.joint_name,
            )
        )
        if len(kept) > MAX_SAMPLES:
            notes.append(
                f"Only the first {MAX_SAMPLES} samples were retained; "
                f"{len(kept) - MAX_SAMPLES} were discarded."
            )
            kept = kept[:MAX_SAMPLES]
        return kept

    @staticmethod
    def _clean_phases(
        phases: list[ObservedMotionPhase],
        notes: list[str],
    ) -> list[ObservedMotionPhase]:
        kept = [
            phase
            for phase in phases
            if phase.start_seconds >= 0 and phase.end_seconds >= phase.start_seconds
        ]
        if len(kept) != len(phases):
            notes.append(
                f"{len(phases) - len(kept)} phase(s) had an impossible time "
                "range and were discarded."
            )
        return kept[:MAX_PHASES]

    @staticmethod
    def _measure(samples: list[ObservedJointAngle]) -> dict[str, float | int]:
        """Report what actually came back, not what was requested."""
        if not samples:
            return {
                "sample_count": 0,
                "distinct_joint_count": 0,
                "observed_span_seconds": 0.0,
                "samples_per_second": 0.0,
                "mean_confidence": 0.0,
                "clear_sample_count": 0,
            }
        times = [sample.timestamp_seconds for sample in samples]
        span = round(max(times) - min(times), 3)
        return {
            "sample_count": len(samples),
            "distinct_joint_count": len(
                {f"{sample.side}.{sample.joint_name}" for sample in samples}
            ),
            "observed_span_seconds": span,
            "samples_per_second": round(len(samples) / span, 3) if span else 0.0,
            "mean_confidence": round(
                sum(sample.confidence for sample in samples) / len(samples),
                3,
            ),
            "clear_sample_count": sum(
                1
                for sample in samples
                if sample.visibility is JointVisibility.CLEAR
            ),
        }
