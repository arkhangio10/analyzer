"""Minimal public routes for the initial APRENDIZ skeleton."""

from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def project_status() -> dict[str, str]:
    """Return the project identity and honest implementation status."""
    return {"project": "APRENDIZ", "status": "initializing"}


@router.get("/health")
async def health() -> dict[str, str]:
    """Return a lightweight process health response."""
    return {"status": "healthy"}
