"""Minimal public routes for the initial APRENDIZ skeleton."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.api.runtime import (
    browser_execution_service,
    computer_execution_service,
    computer_practice_service,
    project_service,
    robot_motion_training_service,
)


router = APIRouter()
WEB_DIR = Path(__file__).resolve().parents[1] / "web"


@router.get("/", response_class=FileResponse)
async def frontend() -> FileResponse:
    """Serve the APRENDIZ product experience."""
    return FileResponse(WEB_DIR / "index.html")


@router.get("/api/status")
async def project_status() -> dict[str, str | bool]:
    """Return the project identity, status, and whether records are durable."""
    return {
        "project": "APRENDIZ",
        "status": "mvp_in_progress",
        "durable_storage": project_service.is_durable,
        "workflow_evidence_durable": all(
            (
                robot_motion_training_service.is_durable,
                computer_practice_service.is_durable,
                computer_execution_service.is_durable,
                browser_execution_service.is_durable,
            )
        ),
    }


@router.get("/health")
async def health() -> dict[str, str]:
    """Return a lightweight process health response."""
    return {"status": "healthy"}
