"""Routes for validation-only computer execution plans."""

from fastapi import APIRouter

from app.models.computer_execution import (
    ComputerPlanValidationRequest,
    ComputerPlanValidationResult,
)
from app.services.computer_execution_service import ComputerExecutionService


router = APIRouter(prefix="/api/execution/computer", tags=["execution"])
computer_execution_service = ComputerExecutionService()


@router.post("/validate", response_model=ComputerPlanValidationResult)
async def validate_computer_plan(
    request: ComputerPlanValidationRequest,
) -> ComputerPlanValidationResult:
    """Validate a plan without touching the host operating system."""
    return computer_execution_service.validate(request)
