"""Routes for validation-only computer execution plans."""

from fastapi import APIRouter, HTTPException, status

from app.api.runtime import browser_execution_service, computer_execution_service
from app.models.browser_execution import (
    ComputerBrowserExecutionRequest,
    ComputerBrowserExecutionResult,
)
from app.models.computer_execution import (
    ComputerPlanValidationRequest,
    ComputerPlanValidationResult,
    ComputerSandboxExecutionRequest,
    ComputerSandboxExecutionResult,
)
from app.services.browser_execution_service import ComputerBrowserExecutionNotFoundError
from app.services.computer_execution_service import (
    ComputerExecutionNotFoundError,
)


router = APIRouter(prefix="/api/execution/computer", tags=["execution"])


@router.post("/validate", response_model=ComputerPlanValidationResult)
async def validate_computer_plan(
    request: ComputerPlanValidationRequest,
) -> ComputerPlanValidationResult:
    """Validate a plan without touching the host operating system."""
    return computer_execution_service.validate(request)


@router.post(
    "/execute",
    response_model=ComputerSandboxExecutionResult,
    status_code=status.HTTP_201_CREATED,
)
async def execute_computer_plan(
    request: ComputerSandboxExecutionRequest,
) -> ComputerSandboxExecutionResult:
    """Execute bounded file actions in the managed local sandbox."""
    return computer_execution_service.execute(request)


@router.get("/executions/{execution_id}", response_model=ComputerSandboxExecutionResult)
async def get_computer_execution(
    execution_id: str,
) -> ComputerSandboxExecutionResult:
    """Retrieve redacted evidence for a local sandbox execution."""
    try:
        return computer_execution_service.get_execution(execution_id)
    except ComputerExecutionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Computer execution was not found.",
        ) from error


@router.post(
    "/browser/execute",
    response_model=ComputerBrowserExecutionResult,
    status_code=status.HTTP_201_CREATED,
)
async def execute_browser_plan(
    request: ComputerBrowserExecutionRequest,
) -> ComputerBrowserExecutionResult:
    """Execute bounded browser actions against explicitly approved public hosts."""
    return await browser_execution_service.execute(request)


@router.get(
    "/browser/executions/{execution_id}",
    response_model=ComputerBrowserExecutionResult,
)
async def get_browser_execution(
    execution_id: str,
) -> ComputerBrowserExecutionResult:
    """Retrieve redacted browser evidence without page or typed-value content."""
    try:
        return browser_execution_service.get_execution(execution_id)
    except ComputerBrowserExecutionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Browser execution was not found.",
        ) from error
