"""Computer plan validation with no host-side execution."""

from pathlib import PurePosixPath, PureWindowsPath
from urllib.parse import urlparse

from app.models.computer_execution import (
    ComputerAction,
    ComputerActionKind,
    ComputerPlanValidationRequest,
    ComputerPlanValidationResult,
)


class ComputerExecutionService:
    """Validate portable UI/file actions before a future sandbox executor."""

    _SENSITIVE_TARGETS = ("password", "passwd", "token", "secret", "api key", "credential")

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
            if action.kind is ComputerActionKind.TYPE_TEXT:
                self._validate_text_input(action, violations)
        return ComputerPlanValidationResult(
            project_id=request.project_id,
            accepted=not violations,
            normalized_actions=normalized,
            violations=list(dict.fromkeys(violations)),
        )

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
