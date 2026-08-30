"""Routes for approved project-video extraction and human review."""

from fastapi import APIRouter, HTTPException, status

from app.api.runtime import project_video_procedure_service
from app.models.project_video_procedure import (
    ProjectVideoProcedureExtractionRequest,
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureReviewRequest,
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
