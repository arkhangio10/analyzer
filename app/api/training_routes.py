"""Training API routes for deterministic procedural-learning slices."""

from fastapi import APIRouter, HTTPException, status

from app.models.evaluation import EvaluationResult
from app.models.robot_motion import (
    RobotMotionEvaluationRequest,
    RobotMotionTrainingRequest,
    RobotMotionTrainingResult,
)
from app.services.robot_motion_training import (
    RobotMotionSessionNotFoundError,
    RobotMotionSessionRejectedError,
    RobotMotionTrainingService,
)


router = APIRouter(prefix="/api/training/robot-motion", tags=["training"])
training_service = RobotMotionTrainingService()


@router.post(
    "",
    response_model=RobotMotionTrainingResult,
    status_code=status.HTTP_201_CREATED,
)
async def train_robot_motion(
    request: RobotMotionTrainingRequest,
) -> RobotMotionTrainingResult:
    """Acquire an inspectable procedure from a simulated motion demonstration."""
    return training_service.train(request)


@router.get("/{session_id}", response_model=RobotMotionTrainingResult)
async def get_robot_motion_training(
    session_id: str,
) -> RobotMotionTrainingResult:
    """Return a stored robot-motion training result."""
    try:
        return training_service.get_result(session_id)
    except RobotMotionSessionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Robot-motion training session was not found.",
        ) from error


@router.post(
    "/{session_id}/evaluate",
    response_model=EvaluationResult,
)
async def evaluate_robot_motion(
    session_id: str,
    request: RobotMotionEvaluationRequest,
) -> EvaluationResult:
    """Evaluate candidate replay data against its instructor demonstration."""
    try:
        return training_service.evaluate(session_id, request)
    except RobotMotionSessionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Robot-motion training session was not found.",
        ) from error
    except RobotMotionSessionRejectedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The instructor demonstration was rejected by safety validation "
                "and cannot be evaluated."
            ),
        ) from error
