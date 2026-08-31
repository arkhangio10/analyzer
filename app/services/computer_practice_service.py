"""Project-bound orchestration for user-approved browser rehearsals."""

from uuid import uuid4

from app.models.browser_execution import ComputerBrowserExecutionRequest
from app.models.computer_execution import ComputerActionKind, ComputerExecutionStatus
from app.models.computer_practice import (
    ComputerPractice,
    ComputerPracticeApprovalRequest,
    ComputerPracticeDraftRequest,
    ComputerPracticeRecord,
    ComputerPracticeRunResult,
    ComputerPracticeStatus,
)
from app.models.project import ComputerExecutionContract
from app.services.browser_execution_service import BrowserExecutionService
from app.services.project_service import ProjectNotFoundError, ProjectService
from app.services.record_store import JsonRecordStore


class ComputerPracticeNotFoundError(LookupError):
    """Raised when a practice does not belong to the requested project."""


class ComputerPracticeConflictError(ValueError):
    """Raised when project state cannot support the requested practice."""


class ComputerPracticeValidationError(ValueError):
    """Raised when a proposed browser plan violates the guarded policy."""

    def __init__(self, violations: list[str]) -> None:
        super().__init__("The browser practice plan is not safe to approve.")
        self.violations = violations


class ComputerPracticeService:
    """Create, approve, execute, and retrieve computer rehearsals."""

    def __init__(
        self,
        project_service: ProjectService,
        browser_execution_service: BrowserExecutionService,
        store: JsonRecordStore | None = None,
    ) -> None:
        self._project_service = project_service
        self._browser_execution_service = browser_execution_service
        self._record_store = store
        records = store.load_all(ComputerPracticeRecord) if store else {}
        self._practices = {
            practice_id: record.practice
            for practice_id, record in records.items()
        }

    @property
    def is_durable(self) -> bool:
        """Report whether redacted practice evidence survives a restart."""
        return bool(self._record_store and self._record_store.is_durable)

    def _retain(self, practice: ComputerPractice) -> ComputerPractice:
        self._practices[practice.practice_id] = practice
        if self._record_store:
            self._record_store.save(
                practice.practice_id,
                self._persistence_record(practice),
            )
        return practice

    @staticmethod
    def _persistence_record(practice: ComputerPractice) -> ComputerPracticeRecord:
        """Remove typed values and URL queries before a practice reaches disk."""
        actions = []
        redacted_ids: list[str] = []
        for action in practice.actions:
            updates: dict[str, str | None] = {}
            if (
                action.kind is ComputerActionKind.TYPE_TEXT
                and action.value_template is not None
            ):
                updates["value_template"] = None
            if action.kind is ComputerActionKind.NAVIGATE:
                redacted_url = BrowserExecutionService._redact_url(action.target)
                if redacted_url and redacted_url != action.target:
                    updates["target"] = redacted_url
            if updates:
                redacted_ids.append(action.action_id)
                actions.append(action.model_copy(update=updates))
            else:
                actions.append(action)

        safe_practice = practice.model_copy(update={"actions": actions})
        if (
            redacted_ids
            and safe_practice.status is ComputerPracticeStatus.AWAITING_APPROVAL
        ):
            safe_practice = safe_practice.model_copy(
                update={
                    "status": ComputerPracticeStatus.BLOCKED,
                    "violations": [
                        *safe_practice.violations,
                        "Private action values were redacted at rest; create and "
                        "approve a new draft before execution.",
                    ],
                }
            )
        return ComputerPracticeRecord(
            practice=safe_practice,
            redacted_action_ids=redacted_ids,
        )

    def create(
        self,
        project_id: str,
        request: ComputerPracticeDraftRequest,
    ) -> ComputerPractice:
        project = self._project_service.get(project_id)
        contract = project.destination_contract
        if not isinstance(contract, ComputerExecutionContract):
            raise ComputerPracticeConflictError(
                "Browser practice is available only for computer projects."
            )
        if not project.is_sufficiently_clear or not contract.application:
            raise ComputerPracticeConflictError(
                "The computer project must be sufficiently clear before practice."
            )
        violations = self._browser_execution_service.validate_plan(
            request.actions,
            request.approved_hosts,
        )
        if violations:
            raise ComputerPracticeValidationError(violations)
        practice = ComputerPractice(
            practice_id=f"cpr_{uuid4().hex[:12]}",
            project_id=project_id,
            application=contract.application,
            procedure_name=request.procedure_name,
            plan_origin=request.plan_origin,
            status=ComputerPracticeStatus.AWAITING_APPROVAL,
            actions=request.actions,
            approved_hosts=request.approved_hosts,
        )
        return self._retain(practice)

    def get(self, project_id: str, practice_id: str) -> ComputerPractice:
        try:
            practice = self._practices[practice_id]
        except KeyError as error:
            raise ComputerPracticeNotFoundError(practice_id) from error
        if practice.project_id != project_id:
            raise ComputerPracticeNotFoundError(practice_id)
        return practice

    async def execute(
        self,
        project_id: str,
        practice_id: str,
        approval: ComputerPracticeApprovalRequest,
    ) -> ComputerPracticeRunResult:
        practice = self.get(project_id, practice_id)
        if practice.status is not ComputerPracticeStatus.AWAITING_APPROVAL:
            raise ComputerPracticeConflictError(
                "This practice has already been executed; create a new draft to retry."
            )
        execution = await self._browser_execution_service.execute(
            ComputerBrowserExecutionRequest(
                project_id=project_id,
                application=practice.application,
                actions=practice.actions,
                approved_hosts=practice.approved_hosts,
                sandbox_required=True,
                acknowledge_external_network=approval.acknowledge_external_network,
                action_timeout_ms=approval.action_timeout_ms,
            )
        )
        status_map = {
            ComputerExecutionStatus.COMPLETED: ComputerPracticeStatus.COMPLETED,
            ComputerExecutionStatus.PARTIALLY_COMPLETED: (
                ComputerPracticeStatus.PARTIALLY_COMPLETED
            ),
            ComputerExecutionStatus.BLOCKED: ComputerPracticeStatus.BLOCKED,
            ComputerExecutionStatus.REJECTED: ComputerPracticeStatus.REJECTED,
        }
        updated = practice.model_copy(
            update={
                "status": status_map[execution.status],
                "violations": execution.violations,
                "latest_execution_id": execution.execution_id,
            }
        )
        self._retain(updated)
        return ComputerPracticeRunResult(practice=updated, execution=execution)
