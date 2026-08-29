"""Minimal public routes for the initial APRENDIZ skeleton."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter()
WEB_DIR = Path(__file__).resolve().parents[1] / "web"


@router.get("/", response_class=FileResponse)
async def frontend() -> FileResponse:
    """Serve the APRENDIZ product experience."""
    return FileResponse(WEB_DIR / "index.html")


@router.get("/api/status")
async def project_status() -> dict[str, str]:
    """Return the project identity and implementation status."""
    return {"project": "APRENDIZ", "status": "mvp_in_progress"}


@router.get("/health")
async def health() -> dict[str, str]:
    """Return a lightweight process health response."""
    return {"status": "healthy"}
