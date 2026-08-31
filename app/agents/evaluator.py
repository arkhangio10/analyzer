"""Externally anchored evaluation agent boundary."""

from app.models.learning import FrozenEvaluationRequest, FrozenEvaluationResult
from app.services.frozen_case_store import FrozenCase


class FrozenCaseNotFoundError(LookupError):
    """Raised when a protected evaluation case is unknown."""


class EvaluatorAgent:
    """Compare outputs while keeping frozen expected answers server-side.

    The agent never writes to its case set, so the learning loop cannot edit
    the answers it is graded against. Every result reports how the expected
    answer was authored, because a pass on a model-generated case is not
    external validation and must never be presented as one.
    """

    def __init__(self, cases: dict[str, FrozenCase] | None = None) -> None:
        self._cases: dict[str, FrozenCase] = dict(cases or {})

    @property
    def case_count(self) -> int:
        """Return how many protected cases are loaded."""
        return len(self._cases)

    @property
    def external_case_count(self) -> int:
        """Return how many cases carry externally authored expected answers."""
        return sum(
            1 for case in self._cases.values() if case.is_external_ground_truth
        )

    def evaluate_frozen(
        self,
        request: FrozenEvaluationRequest,
    ) -> FrozenEvaluationResult:
        """Grade one candidate output without disclosing the answer."""
        try:
            case = self._cases[request.case_id]
        except KeyError as error:
            raise FrozenCaseNotFoundError(request.case_id) from error
        expected = case.expected
        checked = sorted(expected)
        failures = [
            f"Field '{field}' did not match the protected expected result."
            for field in checked
            if request.actual_output.get(field) != expected[field]
        ]
        matched = len(checked) - len(failures)
        return FrozenEvaluationResult(
            evaluation_id=request.evaluation_id,
            skill_id=request.skill_id,
            case_id=request.case_id,
            passed=not failures,
            score=round(matched / len(checked), 6),
            checked_fields=checked,
            failures=failures,
            expected_authored_by=case.authored_by,
            counts_as_external_validation=case.is_external_ground_truth,
        )
