"""Routes for cross-source reconciliation and protected evaluation."""

from fastapi import APIRouter, HTTPException, status

from app.agents.evaluator import FrozenCaseNotFoundError
from app.api.runtime import evaluator
from app.agents.reconciler import ReconcilerAgent
from app.models.learning import (
    FrozenEvaluationRequest,
    FrozenEvaluationResult,
    ReconciliationRequest,
    ReconciliationResult,
)


router = APIRouter(prefix="/api/learning", tags=["learning"])
reconciler = ReconcilerAgent()


@router.post("/reconcile", response_model=ReconciliationResult)
async def reconcile_sources(request: ReconciliationRequest) -> ReconciliationResult:
    """Compare approved procedures without hiding contradictions."""
    return reconciler.reconcile(request)


@router.post("/evaluate/frozen", response_model=FrozenEvaluationResult)
async def evaluate_frozen_case(
    request: FrozenEvaluationRequest,
) -> FrozenEvaluationResult:
    """Evaluate an output without disclosing the protected answer."""
    try:
        return evaluator.evaluate_frozen(request)
    except FrozenCaseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frozen evaluation case was not found.",
        ) from error
