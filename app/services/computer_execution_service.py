"""Computer plan validation with no host-side execution."""

from hashlib import sha256
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import urlparse
from uuid import uuid4

from app.core.config import get_settings
from app.models.computer_execution import (
    ComputerAction,
    ComputerActionExecution,
    ComputerActionKind,
    ComputerActionStatus,
    ComputerExecutionStatus,
    ComputerPlanValidationRequest,
    ComputerPlanValidationResult,
    ComputerSandboxExecutionRequest,
    ComputerSandboxExecutionRecord,
    ComputerSandboxExecutionResult,
)
from app.services.record_store import JsonRecordStore


class ComputerExecutionNotFoundError(LookupError):
    """Raised when a local execution identifier is unknown."""


class ComputerExecutionService:
    """Validate plans and run bounded file operations in a managed sandbox."""

    _SENSITIVE_TARGETS = ("password", "passwd", "token", "secret", "api key", "credential")

    def __init__(
        self,
        sandbox_root: Path | None = None,
        isolation_boundary: str | None = None,
        store: JsonRecordStore | None = None,
    ) -> None:
        self._sandbox_root = sandbox_root or (
            Path(__file__).resolve().parents[2] / ".runtime" / "computer_sandboxes"
        )
        self._isolation_boundary = (
            isolation_boundary or get_settings().computer_execution_boundary
        )
        self._record_store = store
        records = store.load_all(ComputerSandboxExecutionRecord) if store else {}
        self._executions = {
            execution_id: record.execution
            for execution_id, record in records.items()
        }

    @property
    def is_durable(self) -> bool:
        """Report whether redacted execution evidence survives a restart."""
        return bool(self._record_store and self._record_store.is_durable)

    def _retain(
        self,
        result: ComputerSandboxExecutionResult,
    ) -> ComputerSandboxExecutionResult:
        self._executions[result.execution_id] = result
        if self._record_store:
            self._record_store.save(
                result.execution_id,
                ComputerSandboxExecutionRecord(execution=result),
            )
        return result

    def validate(
        self,
        request: ComputerPlanValidationRequest,
    ) -> ComputerPlanValidationResult:
        violations: list[str] = []
        normalized: list[ComputerAction] = []
        seen_ids: set[str] = set()
        for action in request.actions:
            target = " ".join(action.target.split())
            value = action.value_template.strip() if action.value_template else None
            normalized_action = action.model_copy(
                update={"target": target, "value_template": value}
            )
            normalized.append(normalized_action)
            if action.action_id in seen_ids:
                violations.append(f"Duplicate action_id: {action.action_id}.")
            seen_ids.add(action.action_id)
            if action.kind is ComputerActionKind.NAVIGATE:
                self._validate_url(action, violations)
            if action.kind in {
                ComputerActionKind.READ_FILE,
                ComputerActionKind.WRITE_FILE,
            }:
                self._validate_sandbox_path(action, violations)
                if (
                    action.kind is ComputerActionKind.WRITE_FILE
                    and action.value_template is None
                ):
                    violations.append(
                        f"Action {action.action_id}: write_file requires a value template."
                    )
            if action.kind is ComputerActionKind.TYPE_TEXT:
                self._validate_text_input(action, violations)
        return ComputerPlanValidationResult(
            project_id=request.project_id,
            accepted=not violations,
            normalized_actions=normalized,
            violations=list(dict.fromkeys(violations)),
        )

    def execute(
        self,
        request: ComputerSandboxExecutionRequest,
    ) -> ComputerSandboxExecutionResult:
        """Run file actions under one resolved sandbox; block UI automation."""
        validation_request = ComputerPlanValidationRequest(
            project_id=request.project_id,
            application=request.application,
            actions=request.actions,
            sandbox_required=True,
            dry_run=True,
        )
        validation = self.validate(validation_request)
        seed_violations = self._validate_seed_paths(request.input_files)
        violations = [*validation.violations, *seed_violations]
        execution_id = f"cmp_{uuid4().hex[:12]}"
        sandbox_uri = f"sandbox://{execution_id}"
        if violations:
            result = ComputerSandboxExecutionResult(
                execution_id=execution_id,
                project_id=request.project_id,
                status=ComputerExecutionStatus.REJECTED,
                sandbox_uri=sandbox_uri,
                actions=[],
                violations=violations,
                isolation_boundary=self._isolation_boundary,
            )
            return self._retain(result)

        sandbox = (self._sandbox_root / execution_id).resolve()
        sandbox.mkdir(parents=True, exist_ok=False)
        for relative_path, content in request.input_files.items():
            destination = self._resolve_sandbox_path(sandbox, relative_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")

        action_results = [
            self._execute_action(sandbox, action) for action in validation.normalized_actions
        ]
        statuses = {action.status for action in action_results}
        if statuses == {ComputerActionStatus.COMPLETED}:
            status = ComputerExecutionStatus.COMPLETED
        elif statuses == {ComputerActionStatus.BLOCKED}:
            status = ComputerExecutionStatus.BLOCKED
        else:
            status = ComputerExecutionStatus.PARTIALLY_COMPLETED
        result = ComputerSandboxExecutionResult(
            execution_id=execution_id,
            project_id=request.project_id,
            status=status,
            sandbox_uri=sandbox_uri,
            actions=action_results,
            isolation_boundary=self._isolation_boundary,
        )
        return self._retain(result)

    def get_execution(self, execution_id: str) -> ComputerSandboxExecutionResult:
        """Retrieve redacted execution evidence without reading sandbox contents."""
        try:
            return self._executions[execution_id]
        except KeyError as error:
            raise ComputerExecutionNotFoundError(execution_id) from error

    def _execute_action(
        self,
        sandbox: Path,
        action: ComputerAction,
    ) -> ComputerActionExecution:
        if action.kind in {
            ComputerActionKind.NAVIGATE,
            ComputerActionKind.CLICK,
            ComputerActionKind.TYPE_TEXT,
        }:
            return ComputerActionExecution(
                action_id=action.action_id,
                kind=action.kind,
                status=ComputerActionStatus.BLOCKED,
                target=action.target,
                message="Browser actions require the future container browser adapter.",
            )
        target = self._resolve_sandbox_path(sandbox, action.target)
        try:
            if action.kind is ComputerActionKind.WRITE_FILE:
                if action.value_template and action.value_template.startswith("${ENV:"):
                    return ComputerActionExecution(
                        action_id=action.action_id,
                        kind=action.kind,
                        status=ComputerActionStatus.BLOCKED,
                        target=action.target,
                        message="Environment secrets are never resolved by the local sandbox.",
                    )
                content = action.value_template or ""
                encoded = content.encode("utf-8")
                if len(encoded) > 65_536:
                    return ComputerActionExecution(
                        action_id=action.action_id,
                        kind=action.kind,
                        status=ComputerActionStatus.FAILED,
                        target=action.target,
                        message="One write may contain at most 64 KiB.",
                    )
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(encoded)
            else:
                encoded = target.read_bytes()
            return ComputerActionExecution(
                action_id=action.action_id,
                kind=action.kind,
                status=ComputerActionStatus.COMPLETED,
                target=action.target,
                bytes_processed=len(encoded),
                content_sha256=sha256(encoded).hexdigest(),
                message="Sandbox file action completed; content is redacted.",
            )
        except OSError:
            return ComputerActionExecution(
                action_id=action.action_id,
                kind=action.kind,
                status=ComputerActionStatus.FAILED,
                target=action.target,
                message="Sandbox file action failed.",
            )

    def _validate_seed_paths(self, files: dict[str, str]) -> list[str]:
        violations: list[str] = []
        for path in files:
            probe = ComputerAction(
                action_id=f"seed:{path}",
                kind=ComputerActionKind.WRITE_FILE,
                target=path,
                value_template="seed",
            )
            self._validate_sandbox_path(probe, violations)
        return violations

    @staticmethod
    def _resolve_sandbox_path(sandbox: Path, relative_path: str) -> Path:
        target = (sandbox / relative_path.replace("\\", "/")).resolve()
        target.relative_to(sandbox)
        return target

    @staticmethod
    def _validate_url(action: ComputerAction, violations: list[str]) -> None:
        parsed = urlparse(action.target)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            violations.append(
                f"Action {action.action_id}: navigation requires an HTTP(S) URL."
            )
        if parsed.username or parsed.password:
            violations.append(
                f"Action {action.action_id}: credentials cannot be embedded in a URL."
            )

    @staticmethod
    def _validate_sandbox_path(
        action: ComputerAction,
        violations: list[str],
    ) -> None:
        posix = PurePosixPath(action.target.replace("\\", "/"))
        windows = PureWindowsPath(action.target)
        if posix.is_absolute() or windows.is_absolute() or ".." in posix.parts:
            violations.append(
                f"Action {action.action_id}: file paths must stay relative to the sandbox."
            )

    def _validate_text_input(
        self,
        action: ComputerAction,
        violations: list[str],
    ) -> None:
        if action.value_template is None:
            violations.append(
                f"Action {action.action_id}: type_text requires a value template."
            )
            return
        sensitive_target = any(
            marker in action.target.casefold() for marker in self._SENSITIVE_TARGETS
        )
        is_environment_reference = (
            action.value_template.startswith("${ENV:")
            and action.value_template.endswith("}")
        )
        if sensitive_target and not is_environment_reference:
            violations.append(
                f"Action {action.action_id}: sensitive values must use an external environment reference."
            )
