"""Routes for the QC console: what was observed, and what was only claimed.

These routes read. `prove` runs the QC pipeline, which recomputes an audit from
stored samples and initiates no provider call, so nothing here can spend money
on a person's behalf. That is why proving is a POST that costs nothing: it
changes no stored record either, but it is an action a person takes, and the
console should not re-run it on every page load.

The library view degrades in a specific way. When ClickHouse is not reachable
it does not return an empty library, which would read as "nothing wrong here".
It returns what the local record store holds, with `evidence_available` false
and a note saying the library-scale view is the part that is missing.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.agents.qc_pipeline import PipelineDeps, run_qc_pipeline
from app.api.runtime import (
    evidence_store,
    motion_analysis_service,
    project_service,
    project_video_procedure_service,
)
from app.models.motion_analysis import MotionAnalysisRecord
from app.models.qc_pipeline import QcReport
from app.models.qc_view import (
    QcAssetDetail,
    QcAssetSummary,
    QcFindingView,
    QcLibraryView,
    QcSamplePoint,
    QcUntrustedAsset,
    QcVerdictCount,
)
from app.services.motion_analysis_service import MotionAnalysisNotFoundError
from app.services.project_service import ProjectNotFoundError


WEB_DIR = Path(__file__).resolve().parents[1] / "web"

router = APIRouter(tags=["qc"])

EVIDENCE_PRESENT = (
    "Library-scale evidence is served by ClickHouse: the verdict counts and "
    "the untrusted list below were computed by the database, not by this "
    "process."
)
EVIDENCE_ABSENT = (
    "ClickHouse is not configured or not reachable, so the library-scale view "
    "is unavailable. The analyses listed below come from this deployment's own "
    "record store; they are what is retained, not necessarily the whole library."
)

MAX_SERIES_POINTS = 4000


@router.get("/qc", response_class=FileResponse)
async def qc_console() -> FileResponse:
    """Serve the QC console."""
    return FileResponse(WEB_DIR / "qc.html")


def _require_project(project_id: str) -> None:
    try:
        project_service.get(project_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error


def _summary(record: MotionAnalysisRecord) -> QcAssetSummary:
    return QcAssetSummary(
        analysis_id=record.analysis_id,
        extraction_id=record.extraction_id,
        source_url=record.source_url,
        verdict=record.audit.verdict.value,
        sample_count=record.sample_count,
        distinct_joint_count=record.distinct_joint_count,
        created_at=record.created_at,
    )


@router.get("/api/qc/projects/{project_id}/library", response_model=QcLibraryView)
async def qc_library(project_id: str) -> QcLibraryView:
    """Return what is known about one project's analysed video."""
    _require_project(project_id)
    analyses = [
        _summary(record)
        for record in motion_analysis_service.list_for_project(project_id)
    ]

    if not evidence_store.is_available:
        return QcLibraryView(
            project_id=project_id,
            evidence_available=False,
            evidence_note=EVIDENCE_ABSENT,
            analyses=analyses,
        )

    return QcLibraryView(
        project_id=project_id,
        evidence_available=True,
        evidence_note=EVIDENCE_PRESENT,
        verdicts=[
            QcVerdictCount(
                verdict=str(row.get("verdict", "unknown")),
                analyses=int(row.get("analyses") or 0),
                samples=int(row.get("samples") or 0),
                tokens=int(row.get("tokens") or 0),
            )
            for row in evidence_store.library_verdicts(project_id)
        ],
        untrusted=[
            QcUntrustedAsset(
                analysis_id=str(row.get("analysis_id", "")),
                source_url=str(row.get("source_url") or ""),
                verdict=str(row.get("verdict", "unknown")),
                sample_count=int(row.get("sample_count") or 0),
                codes=[str(code) for code in (row.get("codes") or [])][:20],
            )
            for row in evidence_store.untrusted_assets(project_id)
            if row.get("analysis_id")
        ],
        analyses=analyses,
    )


@router.get(
    "/api/qc/projects/{project_id}/analyses/{analysis_id}",
    response_model=QcAssetDetail,
)
async def qc_asset(project_id: str, analysis_id: str) -> QcAssetDetail:
    """Return one analysis with the counts its verdict was reached from."""
    _require_project(project_id)
    try:
        record = motion_analysis_service.get(analysis_id)
    except MotionAnalysisNotFoundError as error:
        raise HTTPException(
            status_code=404, detail="Analysis was not found."
        ) from error
    if record.project_id != project_id:
        raise HTTPException(status_code=404, detail="Analysis was not found.")

    audit = record.audit
    return QcAssetDetail(
        analysis_id=record.analysis_id,
        project_id=record.project_id,
        extraction_id=record.extraction_id,
        source_url=record.source_url,
        verdict=audit.verdict.value,
        physically_measured=record.physically_measured,
        measurement_method=record.measurement_method,
        sample_count=record.sample_count,
        distinct_joint_count=record.distinct_joint_count,
        observed_span_seconds=record.observed_span_seconds,
        samples_per_second=record.samples_per_second,
        mean_confidence=record.mean_confidence,
        clear_sample_count=record.clear_sample_count,
        mirrored_frame_ratio=audit.mirrored_frame_ratio,
        distinct_confidence_values=audit.distinct_confidence_values,
        distinct_visibility_values=audit.distinct_visibility_values,
        acyclic_joints=list(audit.acyclic_joints),
        checked_joint_count=audit.checked_joint_count,
        findings=[
            QcFindingView(
                code=finding.code.value,
                message=finding.message,
                values=dict(finding.values),
            )
            for finding in audit.findings
        ],
        provider=record.provider or "",
        model_version=record.model_version or record.requested_model or "",
        cloud_calls_made=record.cloud_calls_made,
        created_at=record.created_at,
        series=[
            QcSamplePoint(
                joint=sample.joint_name,
                side=sample.side,
                t=sample.timestamp_seconds,
                angle=sample.angle_degrees,
            )
            for sample in record.samples[:MAX_SERIES_POINTS]
        ],
    )


@router.post(
    "/api/qc/projects/{project_id}/extractions/{extraction_id}/prove",
    response_model=QcReport,
)
async def qc_prove(project_id: str, extraction_id: str) -> QcReport:
    """Recompute the audit from stored samples and report what it establishes."""
    _require_project(project_id)
    deps = PipelineDeps(
        project_service=project_service,
        procedure_service=project_video_procedure_service,
        motion_service=motion_analysis_service,
        evidence_store=evidence_store,
    )
    return await run_qc_pipeline(deps, project_id, extraction_id)
