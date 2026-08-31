"""Routes for approved project-video extraction and human review."""

from typing import Literal

from fastapi import APIRouter, HTTPException, status

from app.api.runtime import (
    adaptation_service,
    motion_analysis_service,
    project_reconciliation_service,
    project_service,
    project_video_procedure_service,
)
from app.models.adaptation import DestinationAdaptationPlan
from app.models.motion_analysis import MotionAnalysisRecord, MotionAnalysisRequest
from app.models.learning import ProjectReconciliation
from app.models.procedure_history import ProcedureHistory, ProcedureVersionDiff
from app.models.project_video_procedure import (
    ProjectVideoProcedureExtractionRequest,
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureReviewRequest,
)
from app.services.adaptation_service import AdaptationNotApprovedError
from app.services.gemini_service import (
    GeminiConfigurationError,
    GeminiProviderError,
    GeminiResponseError,
)
from app.services.motion_analysis_service import (
    MotionAnalysisBudgetError,
    MotionAnalysisNotApprovedError,
    MotionAnalysisNotFoundError,
)
from app.services.procedure_history_service import build_history, diff_versions
from app.services.project_reconciliation_service import (
    NotEnoughApprovedSourcesError,
)
from app.services.project_service import ProjectNotFoundError
from app.services.project_video_procedure_service import (
    ProjectVideoProcedureConflictError,
    ProjectVideoProcedureNotFoundError,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/video-procedures",
    tags=["procedures"],
)


@router.post(
    "/extract",
    response_model=ProjectVideoProcedureRecord,
    status_code=status.HTTP_201_CREATED,
)
async def extract_project_video_procedure(
    project_id: str,
    request: ProjectVideoProcedureExtractionRequest,
) -> ProjectVideoProcedureRecord:
    """Run one approved call and retain success or safe failure evidence."""
    try:
        return await project_video_procedure_service.extract(project_id, request)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error


@router.get("", response_model=list[ProjectVideoProcedureRecord])
async def list_project_video_procedures(
    project_id: str,
) -> list[ProjectVideoProcedureRecord]:
    """List every retained extraction for one project, oldest first."""
    try:
        project_service.get(project_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error
    return project_video_procedure_service.list_for_project(project_id)


@router.get("/{extraction_id}", response_model=ProjectVideoProcedureRecord)
async def get_project_video_procedure(
    project_id: str,
    extraction_id: str,
) -> ProjectVideoProcedureRecord:
    """Retrieve one extraction and its current human-review state."""
    try:
        return project_video_procedure_service.get(project_id, extraction_id)
    except ProjectVideoProcedureNotFoundError as error:
        raise HTTPException(status_code=404, detail="Extraction was not found.") from error


@router.post(
    "/{extraction_id}/review",
    response_model=ProjectVideoProcedureRecord,
)
async def review_project_video_procedure(
    project_id: str,
    extraction_id: str,
    request: ProjectVideoProcedureReviewRequest,
) -> ProjectVideoProcedureRecord:
    """Approve or reject a structured procedure without executing it."""
    try:
        return project_video_procedure_service.review(
            project_id,
            extraction_id,
            request,
        )
    except ProjectVideoProcedureNotFoundError as error:
        raise HTTPException(status_code=404, detail="Extraction was not found.") from error
    except ProjectVideoProcedureConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post(
    "/{extraction_id}/adapt",
    response_model=DestinationAdaptationPlan,
)
async def adapt_project_video_procedure(
    project_id: str,
    extraction_id: str,
    language: Literal["es", "en"] = "en",
) -> DestinationAdaptationPlan:
    """Propose a destination plan for an approved procedure without running it."""
    try:
        project = project_service.get(project_id)
        record = project_video_procedure_service.get(project_id, extraction_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error
    except ProjectVideoProcedureNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Extraction was not found.",
        ) from error
    try:
        analysis = motion_analysis_service.latest_for_extraction(extraction_id)
    except MotionAnalysisNotFoundError:
        analysis = None
    try:
        return adaptation_service.adapt(project, record, analysis, language)
    except AdaptationNotApprovedError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


def _load_pair(project_id: str, extraction_id: str):
    """Resolve one project and one of its extractions, or fail with 404."""
    try:
        project = project_service.get(project_id)
        record = project_video_procedure_service.get(project_id, extraction_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error
    except ProjectVideoProcedureNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Extraction was not found.",
        ) from error
    return project, record


@router.post(
    "/{extraction_id}/motion-analysis",
    response_model=MotionAnalysisRecord,
    status_code=status.HTTP_201_CREATED,
)
async def analyze_project_video_motion(
    project_id: str,
    extraction_id: str,
    request: MotionAnalysisRequest,
) -> MotionAnalysisRecord:
    """Spend one acknowledged cloud call sampling approved video for movement."""
    project, record = _load_pair(project_id, extraction_id)
    try:
        return await motion_analysis_service.analyze(project, record, request)
    except MotionAnalysisNotApprovedError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except MotionAnalysisBudgetError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except GeminiConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except GeminiProviderError as error:
        raise HTTPException(
            status_code=502,
            detail=f"{error} The call was attempted and may have been billed.",
        ) from error
    except GeminiResponseError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.get(
    "/{extraction_id}/motion-analysis",
    response_model=MotionAnalysisRecord,
)
async def get_project_video_motion_analysis(
    project_id: str,
    extraction_id: str,
) -> MotionAnalysisRecord:
    """Return the newest retained motion analysis without spending anything."""
    _load_pair(project_id, extraction_id)
    try:
        return motion_analysis_service.latest_for_extraction(extraction_id)
    except MotionAnalysisNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="No motion analysis has been run for this extraction.",
        ) from error


@router.get("/history/versions", response_model=ProcedureHistory)
async def get_project_procedure_history(project_id: str) -> ProcedureHistory:
    """List every retained version and diff the two most recent."""
    try:
        project_service.get(project_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error
    return build_history(
        project_id,
        project_video_procedure_service.list_for_project(project_id),
    )


@router.get(
    "/history/diff/{from_extraction_id}/{to_extraction_id}",
    response_model=ProcedureVersionDiff,
)
async def diff_project_procedure_versions(
    project_id: str,
    from_extraction_id: str,
    to_extraction_id: str,
) -> ProcedureVersionDiff:
    """Report what changed between two retained versions without altering them."""
    _, earlier = _load_pair(project_id, from_extraction_id)
    _, later = _load_pair(project_id, to_extraction_id)
    return diff_versions(earlier, later)


@router.get("/history/reconciliation", response_model=ProjectReconciliation)
async def reconcile_project_procedures(project_id: str) -> ProjectReconciliation:
    """Compare every approved procedure and report how independent they are."""
    try:
        project = project_service.get(project_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error
    try:
        return project_reconciliation_service.reconcile(
            project_id,
            project_video_procedure_service.list_for_project(project_id),
            project.task_definition.task_name,
        )
    except NotEnoughApprovedSourcesError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
