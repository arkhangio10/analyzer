"""Routes for simulation-first robot profile normalization."""

from fastapi import APIRouter, HTTPException, status

from app.models.robot_profile import (
    ARP1MotionContract,
    ARP1RobotProfile,
    URDFImportRequest,
)
from app.services.robot_profile_service import (
    RobotDescriptionError,
    RobotProfileService,
)


router = APIRouter(prefix="/api/robots/profiles/arp-1", tags=["robot profiles"])
robot_profile_service = RobotProfileService()


@router.post("/import/urdf", response_model=ARP1RobotProfile)
async def import_urdf_profile(request: URDFImportRequest) -> ARP1RobotProfile:
    """Normalize a bounded URDF document without starting a simulator."""
    try:
        return robot_profile_service.import_urdf(request)
    except RobotDescriptionError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


@router.post("/motion-contract", response_model=ARP1MotionContract)
async def create_motion_contract(profile: ARP1RobotProfile) -> ARP1MotionContract:
    """Convert compatible ARP-1 joints into the current trainer contract."""
    return robot_profile_service.to_motion_contract(profile)
