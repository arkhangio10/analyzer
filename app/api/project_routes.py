"""Routes for project clarification and destination configuration."""

from fastapi import APIRouter, HTTPException, status

from app.api.runtime import project_service
from app.models.project import ProjectClarificationRequest, ProjectDraft
from app.services.project_service import ProjectNotFoundError


router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectDraft, status_code=status.HTTP_201_CREATED)
async def create_project(request: ProjectClarificationRequest) -> ProjectDraft:
    """Create a project while asking no more than one critical question."""
    return project_service.create(request)


@router.get("", response_model=list[ProjectDraft])
async def list_projects() -> list[ProjectDraft]:
    """List retained project drafts so earlier work can be reopened."""
    return project_service.list_projects()


@router.get("/{project_id}", response_model=ProjectDraft)
async def get_project(project_id: str) -> ProjectDraft:
    """Retrieve an existing local project draft."""
    try:
        return project_service.get(project_id)
    except ProjectNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project was not found.",
        ) from error
