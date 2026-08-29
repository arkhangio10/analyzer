"""Guarded Playwright execution for explicitly approved public hosts."""

from __future__ import annotations

import asyncio
from hashlib import sha256
from ipaddress import ip_address
import socket
from urllib.parse import urlparse, urlunparse
from uuid import uuid4

from app.core.config import get_settings
from app.models.browser_execution import (
    ComputerBrowserActionExecution,
    ComputerBrowserExecutionRequest,
    ComputerBrowserExecutionResult,
)
from app.models.computer_execution import (
    ComputerAction,
    ComputerActionKind,
    ComputerActionStatus,
    ComputerExecutionStatus,
)

try:
    from playwright.async_api import (
        Error as PlaywrightError,
        Route,
        TimeoutError as PlaywrightTimeoutError,
        WebSocketRoute,
        async_playwright,
    )
except ImportError:  # pragma: no cover - exercised by the disabled-adapter path
    PlaywrightError = RuntimeError
    PlaywrightTimeoutError = TimeoutError
    Route = object
    WebSocketRoute = object
    async_playwright = None


class ComputerBrowserExecutionNotFoundError(LookupError):
    """Raised when a browser execution identifier is unknown."""


class PublicHostPolicy:
    """Allow exact approved hosts only when DNS resolves to public addresses."""

    def __init__(self, approved_hosts: list[str]) -> None:
        self.approved_hosts = set(approved_hosts)
        self._resolution_cache: dict[str, bool] = {}

    @staticmethod
    def validate_host_syntax(host: str) -> str | None:
        if (
            len(host) > 253
            or "://" in host
            or "/" in host
            or "@" in host
            or any(character.isspace() for character in host)
        ):
            return "must be a hostname without scheme, path, credentials, or whitespace"
        try:
            host.encode("idna")
        except UnicodeError:
            return "is not a valid internationalized hostname"
        try:
            address = ip_address(host)
        except ValueError:
            return None
        if not address.is_global:
            return "must not be a private, loopback, link-local, or reserved address"
        return None

    def validate_url_syntax(self, url: str) -> str | None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return "requires an HTTP(S) URL"
        if parsed.username or parsed.password:
            return "cannot embed credentials in a URL"
        try:
            port = parsed.port
        except ValueError:
            return "contains an invalid port"
        expected_port = 80 if parsed.scheme == "http" else 443
        if port not in {None, expected_port}:
            return f"port {port} is outside the approved web port policy"
        host = parsed.hostname.casefold().rstrip(".")
        if host not in self.approved_hosts:
            return f"host {host} is not explicitly approved"
        return None

    async def permits_url(self, url: str) -> bool:
        if self.validate_url_syntax(url) is not None:
            return False
        parsed = urlparse(url)
        assert parsed.hostname is not None
        host = parsed.hostname.casefold().rstrip(".")
        if host not in self.approved_hosts:
            return False
        if host not in self._resolution_cache:
            self._resolution_cache[host] = await asyncio.to_thread(
                self._resolves_only_to_public_addresses,
                host,
            )
        return self._resolution_cache[host]

    @staticmethod
    def _resolves_only_to_public_addresses(host: str) -> bool:
        try:
            addresses = {
                entry[4][0]
                for entry in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
            }
        except socket.gaierror:
            return False
        if not addresses:
            return False
        return all(ip_address(address).is_global for address in addresses)


class BrowserExecutionService:
    """Validate and run a bounded sequence in one disposable browser context."""

    _BROWSER_KINDS = {
        ComputerActionKind.NAVIGATE,
        ComputerActionKind.CLICK,
        ComputerActionKind.TYPE_TEXT,
    }
    _SENSITIVE_TARGETS = (
        "password",
        "passwd",
        "token",
        "secret",
        "api key",
        "credential",
    )

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        isolation_boundary: str | None = None,
    ) -> None:
        settings = get_settings()
        self._enabled = settings.computer_browser_enabled if enabled is None else enabled
        self._isolation_boundary = (
            isolation_boundary or settings.computer_execution_boundary
        )
        self._executions: dict[str, ComputerBrowserExecutionResult] = {}

    async def execute(
        self,
        request: ComputerBrowserExecutionRequest,
    ) -> ComputerBrowserExecutionResult:
        execution_id = f"brw_{uuid4().hex[:12]}"
        policy = PublicHostPolicy(request.approved_hosts)
        violations = self._validate(request, policy)
        adapter_available = bool(self._enabled and async_playwright is not None)
        if not adapter_available:
            violations.append(
                "The guarded browser adapter is disabled or Playwright is unavailable."
            )
        if self._isolation_boundary != "application_container":
            violations.append(
                "Browser execution requires the application_container boundary."
            )
        if violations:
            return self._store(
                ComputerBrowserExecutionResult(
                    execution_id=execution_id,
                    project_id=request.project_id,
                    status=ComputerExecutionStatus.REJECTED,
                    actions=[],
                    violations=list(dict.fromkeys(violations)),
                    approved_hosts=request.approved_hosts,
                    browser_adapter_available=adapter_available,
                    isolation_boundary=self._isolation_boundary,
                )
            )

        try:
            result = await self._run_playwright(execution_id, request, policy)
        except (PlaywrightTimeoutError, PlaywrightError, OSError):
            result = ComputerBrowserExecutionResult(
                execution_id=execution_id,
                project_id=request.project_id,
                status=ComputerExecutionStatus.BLOCKED,
                actions=[],
                violations=["The disposable browser could not start or complete safely."],
                approved_hosts=request.approved_hosts,
                browser_adapter_available=True,
                isolation_boundary=self._isolation_boundary,
            )
        return self._store(result)

    def get_execution(self, execution_id: str) -> ComputerBrowserExecutionResult:
        try:
            return self._executions[execution_id]
        except KeyError as error:
            raise ComputerBrowserExecutionNotFoundError(execution_id) from error

    def _validate(
        self,
        request: ComputerBrowserExecutionRequest,
        policy: PublicHostPolicy,
    ) -> list[str]:
        violations: list[str] = []
        for host in request.approved_hosts:
            problem = policy.validate_host_syntax(host)
            if problem:
                violations.append(f"Approved host {host}: {problem}.")

        has_navigated = False
        seen_ids: set[str] = set()
        for action in request.actions:
            if action.action_id in seen_ids:
                violations.append(f"Duplicate action_id: {action.action_id}.")
            seen_ids.add(action.action_id)
            if action.kind not in self._BROWSER_KINDS:
                violations.append(
                    f"Action {action.action_id}: file actions are not accepted "
                    "by the browser endpoint."
                )
                continue
            if action.kind is ComputerActionKind.NAVIGATE:
                has_navigated = True
                problem = policy.validate_url_syntax(action.target)
                if problem:
                    violations.append(f"Action {action.action_id}: {problem}.")
            elif not has_navigated:
                violations.append(
                    f"Action {action.action_id}: navigation must occur before "
                    "page interaction."
                )
            if action.kind is ComputerActionKind.TYPE_TEXT:
                self._validate_text_action(action, violations)
        return violations

    def _validate_text_action(
        self,
        action: ComputerAction,
        violations: list[str],
    ) -> None:
        if action.value_template is None:
            violations.append(
                f"Action {action.action_id}: type_text requires a value template."
            )
            return
        if "${ENV:" in action.value_template:
            violations.append(
                f"Action {action.action_id}: environment values are never "
                "resolved by the browser adapter."
            )
        if any(marker in action.target.casefold() for marker in self._SENSITIVE_TARGETS):
            violations.append(
                f"Action {action.action_id}: sensitive form fields are not "
                "supported in this phase."
            )

    async def _run_playwright(
        self,
        execution_id: str,
        request: ComputerBrowserExecutionRequest,
        policy: PublicHostPolicy,
    ) -> ComputerBrowserExecutionResult:
        action_results: list[ComputerBrowserActionExecution] = []
        network_requests = 0
        blocked_requests = 0

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(
                accept_downloads=False,
                service_workers="block",
            )
            await context.add_init_script(
                """
                Object.defineProperty(globalThis, 'RTCPeerConnection', {
                  value: undefined,
                  configurable: false
                });
                Object.defineProperty(globalThis, 'webkitRTCPeerConnection', {
                  value: undefined,
                  configurable: false
                });
                """
            )

            async def enforce_network_policy(route: Route) -> None:
                nonlocal network_requests, blocked_requests
                if await policy.permits_url(route.request.url):
                    network_requests += 1
                    await route.continue_()
                else:
                    blocked_requests += 1
                    await route.abort("blockedbyclient")

            await context.route("**/*", enforce_network_policy)

            async def block_websocket(websocket: WebSocketRoute) -> None:
                nonlocal blocked_requests
                blocked_requests += 1
                await websocket.close(
                    code=1008,
                    reason="WebSockets are disabled by the approved-host policy.",
                )

            await context.route_web_socket("**/*", block_websocket)
            page = await context.new_page()
            for action in request.actions:
                blocked_before_action = blocked_requests
                try:
                    if action.kind is ComputerActionKind.NAVIGATE:
                        await page.goto(
                            action.target,
                            wait_until="domcontentloaded",
                            timeout=request.action_timeout_ms,
                        )
                    elif action.kind is ComputerActionKind.CLICK:
                        await page.locator(action.target).click(
                            timeout=request.action_timeout_ms
                        )
                    else:
                        await page.locator(action.target).fill(
                            action.value_template or "",
                            timeout=request.action_timeout_ms,
                        )
                    title = await page.title()
                    action_blocked = blocked_requests > blocked_before_action
                    action_results.append(
                        ComputerBrowserActionExecution(
                            action_id=action.action_id,
                            kind=action.kind,
                            status=(
                                ComputerActionStatus.BLOCKED
                                if action_blocked
                                else ComputerActionStatus.COMPLETED
                            ),
                            target=self._redact_target(action),
                            observed_url=self._redact_url(page.url),
                            page_title_sha256=(
                                sha256(title.encode("utf-8")).hexdigest()
                                if title
                                else None
                            ),
                            page_title_length=len(title),
                            message=(
                                "Browser action triggered a network request "
                                "outside the approved policy."
                                if action_blocked
                                else "Browser action completed; page content and "
                                "typed values are redacted."
                            ),
                        )
                    )
                except (PlaywrightTimeoutError, PlaywrightError):
                    action_results.append(
                        ComputerBrowserActionExecution(
                            action_id=action.action_id,
                            kind=action.kind,
                            status=ComputerActionStatus.FAILED,
                            target=self._redact_target(action),
                            observed_url=self._redact_url(page.url),
                            message=(
                                "Browser action failed or exceeded its bounded "
                                "timeout."
                            ),
                        )
                    )
            await context.close()
            await browser.close()

        statuses = {action.status for action in action_results}
        if statuses == {ComputerActionStatus.COMPLETED}:
            status = ComputerExecutionStatus.COMPLETED
        elif statuses and statuses <= {
            ComputerActionStatus.BLOCKED,
            ComputerActionStatus.FAILED,
        }:
            status = ComputerExecutionStatus.BLOCKED
        else:
            status = ComputerExecutionStatus.PARTIALLY_COMPLETED
        return ComputerBrowserExecutionResult(
            execution_id=execution_id,
            project_id=request.project_id,
            status=status,
            actions=action_results,
            approved_hosts=request.approved_hosts,
            external_network_requests=network_requests,
            blocked_network_requests=blocked_requests,
            browser_adapter_available=True,
            isolation_boundary=self._isolation_boundary,
        )

    def _store(
        self,
        result: ComputerBrowserExecutionResult,
    ) -> ComputerBrowserExecutionResult:
        self._executions[result.execution_id] = result
        return result

    @staticmethod
    def _redact_url(url: str) -> str | None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return None
        netloc = parsed.hostname
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        return urlunparse((parsed.scheme, netloc, parsed.path, "", "", ""))

    @classmethod
    def _redact_target(cls, action: ComputerAction) -> str:
        if action.kind is ComputerActionKind.NAVIGATE:
            return cls._redact_url(action.target) or "redacted://invalid"
        return action.target
