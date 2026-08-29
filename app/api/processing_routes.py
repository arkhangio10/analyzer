"""Routes for frontend-visible backend processing sessions."""

from fastapi import APIRouter, HTTPException, status

from app.models.processing import (
    RobotMotionProcessingRequest,
    RobotMotionProcessingSession,
)
from app.services.processing_service import (
    ProcessingSessionNotFoundError,
    RobotMotionProcessingService,
)


router = APIRouter(prefix="/api/processing/robot-motion", tags=["processing"])
processing_service = RobotMotionProcessingService()


@router.post(
    "",
    response_model=RobotMotionProcessingSession,
    status_code=status.HTTP_201_CREATED,
)
async def start_robot_motion_processing(
    request: RobotMotionProcessingRequest,
) -> RobotMotionProcessingSession:
    """Start the safe local processing demonstration used by the UI."""
    return processing_service.start(request)


@router.get("/{session_id}", response_model=RobotMotionProcessingSession)
async def get_robot_motion_processing(
    session_id: str,
) -> RobotMotionProcessingSession:
    """Return current state for a frontend processing session."""
    try:
        return processing_service.get(session_id)
    except ProcessingSessionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing session was not found.",
        ) from error

