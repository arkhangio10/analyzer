"""Routes for project-bound, user-approved browser rehearsals."""

from fastapi import APIRouter, HTTPException, status

from app.api.runtime import computer_practice_service
from app.models.computer_practice import (
    ComputerPractice,
    ComputerPracticeApprovalRequest,
    ComputerPracticeDraftRequest,
    ComputerPracticeRunResult,
)
from app.services.computer_practice_service import (
    ComputerPracticeConflictError,
    ComputerPracticeNotFoundError,
    ComputerPracticeValidationError,
)
from app.services.project_service import ProjectNotFoundError


router = APIRouter(prefix="/api/projects/{project_id}/computer-practices", tags=["practice"])


@router.post("", response_model=ComputerPractice, status_code=status.HTTP_201_CREATED)
async def create_computer_practice(
    project_id: str,
    request: ComputerPracticeDraftRequest,
) -> ComputerPractice:
    """Create an approvable plan without launching a browser."""
    try:
        return computer_practice_service.create(project_id, request)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project was not found.") from error
    except ComputerPracticeConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ComputerPracticeValidationError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "The browser practice plan is not safe to approve.",
                "violations": error.violations,
            },
        ) from error


@router.get("/{practice_id}", response_model=ComputerPractice)
async def get_computer_practice(
    project_id: str,
    practice_id: str,
) -> ComputerPractice:
    """Retrieve the approved-host plan and its current state."""
    try:
        return computer_practice_service.get(project_id, practice_id)
    except ComputerPracticeNotFoundError as error:
        raise HTTPException(status_code=404, detail="Practice was not found.") from error


@router.post(
    "/{practice_id}/execute",
    response_model=ComputerPracticeRunResult,
    status_code=status.HTTP_201_CREATED,
)
async def execute_computer_practice(
    project_id: str,
    practice_id: str,
    approval: ComputerPracticeApprovalRequest,
) -> ComputerPracticeRunResult:
    """Execute a previously stored plan after explicit human approval."""
    try:
        return await computer_practice_service.execute(project_id, practice_id, approval)
    except ComputerPracticeNotFoundError as error:
        raise HTTPException(status_code=404, detail="Practice was not found.") from error
    except ComputerPracticeConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
