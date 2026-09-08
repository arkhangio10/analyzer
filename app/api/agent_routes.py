"""What an exported agent knows, served from the skill it was packaged with.

These routes exist in every deployment so a client can ask whether it is
talking to an exported agent. Outside agent mode `/api/skill` is a 404 rather
than an empty skill, because an empty skill would read as an agent that
learned nothing.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from app.api.runtime import evaluator
from app.core.config import get_settings
from app.models.agent_package import ExportedAgentSkill


router = APIRouter(tags=["agent"])


def _load_skill() -> ExportedAgentSkill:
    settings = get_settings()
    if not settings.agent_mode or not settings.skill_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This service is not running as an exported agent.",
        )
    path = Path(settings.skill_path)
    try:
        return ExportedAgentSkill.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"The skill file is missing at {path}.",
        ) from error
    except ValidationError as error:
        # A skill that fails its own guarantees is refused, not served.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The skill file does not satisfy the exported-agent contract.",
        ) from error


@router.get("/api/skill", response_model=ExportedAgentSkill)
async def read_skill() -> ExportedAgentSkill:
    """Return everything this agent knows, with its lineage and guarantees."""
    return _load_skill()


@router.get("/api/agent")
async def agent_status() -> dict[str, object]:
    """Report whether this is an exported agent and what it carries."""
    settings = get_settings()
    body: dict[str, object] = {
        "agent_mode": settings.agent_mode,
        "skill_loaded": False,
        "frozen_case_count": evaluator.case_count,
        "external_case_count": evaluator.external_case_count,
    }
    if not settings.agent_mode:
        return body
    try:
        skill = _load_skill()
    except HTTPException as error:
        body["skill_error"] = error.detail
        return body
    body.update(
        skill_loaded=True,
        language=skill.language,
        destination=skill.destination.value,
        procedure_version=skill.procedure_version,
        step_count=len(skill.skill.procedure.steps),
        name=skill.skill.name,
        exported_at=skill.exported_at.isoformat(),
        guarantees=skill.guarantees.model_dump(),
    )
    return body
