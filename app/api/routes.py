"""Minimal public routes for the initial APRENDIZ skeleton."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.api.spend_guard import (
    spend_endpoints_are_protected,
    spend_token_is_required,
)
from app.core.config import get_settings
from app.api.runtime import (
    browser_execution_service,
    spend_ledger,
    computer_execution_service,
    computer_practice_service,
    project_service,
    robot_motion_training_service,
)


router = APIRouter()
WEB_DIR = Path(__file__).resolve().parents[1] / "web"


@router.get("/", response_class=FileResponse)
async def frontend() -> FileResponse:
    """Serve the product experience, or an exported agent's own interface."""
    page = "agent.html" if get_settings().agent_mode else "index.html"
    return FileResponse(WEB_DIR / page)


@router.get("/api/status")
async def project_status() -> dict[str, object]:
    """Return the project identity, status, and whether records are durable."""
    return {
        "project": "APRENDIZ",
        "status": "mvp_in_progress",
        # A writable directory is not durability on a container that is
        # replaced. Both facts are reported, because they differ there.
        "durable_storage": project_service.is_durable
        and get_settings().records_survive_restart,
        "records_survive_restart": get_settings().records_survive_restart,
        # Whether an unknown caller can reach an endpoint that spends money.
        "spend_endpoints_protected": spend_endpoints_are_protected(),
        # Whether this deployment expects the spend token header, so the
        # console can ask for it before spending rather than after failing.
        "spend_token_required": spend_token_is_required(),
        # What the application has spent against its own ceiling this period.
        "spend": spend_ledger.state().model_dump(mode="json"),
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
