"""Private NAS runtime HTTP server for the research dashboard.

The server intentionally uses the Python standard library. It wraps the
Phase96/97 NAS app shell so the DS925+ container can serve the research
dashboard without adding a new web-framework dependency in this phase.
"""

from __future__ import annotations

from argparse import ArgumentParser
from collections import deque
from dataclasses import dataclass, field
import hashlib
import hmac
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from threading import Lock
import time
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    DEFAULT_ACTIVE_REGISTRY_PATH,
    NasDeclaredPhaseStartError,
    apply_nas_declared_phase_start_update,
    build_nas_declared_phase_start_status,
    preview_nas_declared_phase_start_update,
    rollback_nas_declared_phase_start_update,
)
from business_cycle.render.nas_declared_phase_start import (
    render_nas_declared_phase_start_page,
)
from business_cycle.render.nas_source_operations import (
    build_nas_source_operations_api,
    render_nas_source_operations_page,
)
from business_cycle.service.nas_app_shell import (
    NasAppRequest,
    build_nas_app_shell,
    dispatch_nas_app_request,
)
from business_cycle.service.nas_live_dashboard import build_nas_live_dashboard_runtime

DEFAULT_SESSION_HEADER = "X-Business-Cycle-Session"
SESSION_COOKIE_NAME = "business_cycle_private_session"
LOCAL_HEALTH_PATHS = {"/healthz", "/readyz"}
MAX_LOGIN_BODY_BYTES = 4096
DEFAULT_LOGIN_MAX_FAILURES = 5
DEFAULT_LOGIN_WINDOW_SECONDS = 300
DEFAULT_DASHBOARD_SHELL_TTL_SECONDS = 900


class LoginAttemptLimiter:
    """Small in-memory failed-login limiter for the private NAS entry point."""

    def __init__(
        self,
        *,
        max_failures: int = DEFAULT_LOGIN_MAX_FAILURES,
        window_seconds: int = DEFAULT_LOGIN_WINDOW_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_failures < 1 or window_seconds < 1:
            raise ValueError("login limiter values must be positive")
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self._clock = clock
        self._failures: dict[str, deque[float]] = {}
        self._lock = Lock()

    @classmethod
    def from_environment(cls) -> LoginAttemptLimiter:
        """Build the limiter from optional deployment environment values."""

        return cls(
            max_failures=_positive_env_int(
                "BUSINESS_CYCLE_LOGIN_MAX_FAILURES",
                DEFAULT_LOGIN_MAX_FAILURES,
            ),
            window_seconds=_positive_env_int(
                "BUSINESS_CYCLE_LOGIN_WINDOW_SECONDS",
                DEFAULT_LOGIN_WINDOW_SECONDS,
            ),
        )

    def is_blocked(self, client_key: str) -> bool:
        """Return whether the client exhausted its failed-login allowance."""

        with self._lock:
            failures = self._active_failures(client_key)
            return len(failures) >= self.max_failures

    def record_failure(self, client_key: str) -> None:
        """Record one failed login for a client without storing submitted data."""

        with self._lock:
            failures = self._active_failures(client_key)
            failures.append(self._clock())

    def clear(self, client_key: str) -> None:
        """Clear failed attempts after a successful login."""

        with self._lock:
            self._failures.pop(client_key, None)

    def retry_after_seconds(self, client_key: str) -> int:
        """Return a conservative retry delay for a blocked client."""

        with self._lock:
            failures = self._active_failures(client_key)
            if len(failures) < self.max_failures:
                return 0
            elapsed = self._clock() - failures[0]
            return max(1, int(self.window_seconds - elapsed) + 1)

    def _active_failures(self, client_key: str) -> deque[float]:
        now = self._clock()
        cutoff = now - self.window_seconds
        failures = self._failures.setdefault(client_key, deque())
        while failures and failures[0] <= cutoff:
            failures.popleft()
        if not failures:
            self._failures[client_key] = failures
        return failures


class NasAppShellTtlCache:
    """Cache expensive live Postgres materialization and refresh it safely."""

    def __init__(
        self,
        builder: Callable[[], dict[str, Any]],
        *,
        ttl_seconds: int = DEFAULT_DASHBOARD_SHELL_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if ttl_seconds < 1:
            raise ValueError("dashboard shell TTL must be positive")
        self._builder = builder
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._lock = Lock()
        self._shell = builder()
        self._built_at = clock()
        self.refresh_count = 1
        self.refresh_error_count = 0

    def get(self) -> dict[str, Any]:
        if self._clock() - self._built_at < self._ttl_seconds:
            return self._shell
        with self._lock:
            if self._clock() - self._built_at < self._ttl_seconds:
                return self._shell
            try:
                self._shell = self._builder()
                self._built_at = self._clock()
                self.refresh_count += 1
                return self._shell
            except Exception:  # noqa: BLE001 - retain last good private snapshot
                self.refresh_error_count += 1
                self._built_at = self._clock()
                stale = dict(self._shell)
                stale["trust_metadata"] = dict(stale.get("trust_metadata", {})) | {
                    "dashboard_snapshot_status": "stale_after_refresh_error",
                    "dashboard_shell_refresh_error_count": self.refresh_error_count,
                }
                self._shell = stale
                return self._shell

    def invalidate(self) -> None:
        """Force the next request to rematerialize the dashboard shell."""

        with self._lock:
            self._built_at = float("-inf")


@dataclass(frozen=True)
class RuntimeResponse:
    """Small response object shared by tests and the HTTP handler."""

    status_code: int
    content_type: str
    body: str
    route_id: str | None = None
    headers: dict[str, str] = field(default_factory=dict)


def build_runtime_response(
    *,
    path: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    session_secret: str | None = None,
    shell: dict[str, Any] | None = None,
    body: str = "",
    cycle_state_registry_path: str | None = None,
) -> RuntimeResponse:
    """Return a private NAS runtime response without binding a network port."""

    normalized_path = urlparse(path).path or "/"
    headers = _normalize_headers(headers or {})
    if normalized_path == "/login":
        return _login_response(
            method=method,
            body=body,
            headers=headers,
            session_secret=session_secret,
        )
    if normalized_path == "/logout":
        return _redirect_response(
            "/login",
            extra_headers={
                "Set-Cookie": _session_cookie(
                    "",
                    max_age=0,
                    secure=_secure_cookie_for_request(headers),
                ),
            },
        )
    if normalized_path == "/healthz":
        return _json_response(
            200,
            {
                "status": "ok",
                "service": "business_cycle_private_nas",
                "research_only": True,
                "public_exposure": False,
            },
        )
    if normalized_path == "/readyz":
        shell = shell or build_nas_app_shell()
        trust = shell.get("trust_metadata", {})
        return _json_response(
            200,
            {
                "status": "ready",
                "route_count": shell["route_count"],
                "dashboard_data_source": trust.get(
                    "dashboard_data_source",
                    "bundled_rehearsal_snapshot",
                ),
                "live_db_connected": bool(trust.get("live_db_connected", False)),
                "snapshot_as_of": trust.get("snapshot_as_of"),
                "database_latest_observation_date": trust.get(
                    "database_latest_observation_date",
                ),
                "refresh_state": trust.get("refresh_state", "not_configured"),
                "source_refresh_health_status": trust.get(
                    "source_refresh_health_status",
                    "not_configured",
                ),
                "dashboard_snapshot_status": trust.get(
                    "dashboard_snapshot_status",
                    "current_cached_snapshot",
                ),
                "governed_cycle_state_operator_route_count": 5,
                "source_operations_route_count": 2,
                "portfolio_replay_route_count": 4,
                "strict_replay_backtest_status": trust.get(
                    "strict_replay_backtest_status", "not_started"
                ),
                "research_backtest_result_count": trust.get(
                    "research_backtest_result_count", 0
                ),
                "strict_replay_retained_snapshot_count": trust.get(
                    "strict_replay_retained_snapshot_count", 0
                ),
                "nas_v1_operational_acceptance_status": trust.get(
                    "nas_v1_operational_acceptance_status", "not_started"
                ),
                "nas_v1_operational_acceptance_passed": bool(
                    trust.get("nas_v1_operational_acceptance_passed", False)
                ),
                "prospective_wait_state": trust.get(
                    "prospective_wait_state", "not_configured"
                ),
                "prospective_protocol_started": bool(
                    trust.get("prospective_protocol_started", False)
                ),
                "prospective_registry_record_count": int(
                    trust.get("prospective_registry_record_count", 0)
                ),
                "real_registry_write_attempt_count": int(
                    trust.get("real_registry_write_attempt_count", 0)
                ),
                "prospective_validation_seal_ready": bool(
                    trust.get("prospective_validation_seal_ready", False)
                ),
                "release_family_count": trust.get("release_family_count", 0),
                "research_only": True,
                "public_exposure": False,
            },
        )
    normalized_method = method.upper()
    if normalized_method not in {"GET", "POST"}:
        return _json_response(405, {"error": "method_not_allowed", "research_only": True})

    secret = session_secret if session_secret is not None else _session_secret()
    if not secret:
        return _json_response(
            503,
            {
                "error": "session_secret_not_configured",
                "research_only": True,
                "private_nas_only": True,
            },
        )
    if not _authorized(headers, secret):
        if _prefers_html(headers):
            return _redirect_response("/login")
        return _json_response(
            401,
            {
                "error": "unauthorized",
                "research_only": True,
                "private_nas_only": True,
            },
        )

    cycle_state_response = _cycle_state_response(
        path=normalized_path,
        method=normalized_method,
        body=body,
        active_registry_path=(
            cycle_state_registry_path
            or os.environ.get("BUSINESS_CYCLE_DECLARED_CYCLE_STATE_PATH")
            or str(DEFAULT_ACTIVE_REGISTRY_PATH)
        ),
    )
    if cycle_state_response is not None:
        return cycle_state_response
    source_operations_response = _source_operations_response(
        path=normalized_path,
        method=normalized_method,
        shell=shell,
    )
    if source_operations_response is not None:
        return source_operations_response
    technology_response = _technology_cycle_response(
        path=normalized_path,
        method=normalized_method,
        shell=shell,
    )
    if technology_response is not None:
        return technology_response
    portfolio_replay_response = _portfolio_replay_response(
        path=normalized_path,
        method=normalized_method,
        shell=shell,
    )
    if portfolio_replay_response is not None:
        return portfolio_replay_response
    prospective_response = _prospective_validation_response(
        path=normalized_path,
        method=normalized_method,
        shell=shell,
    )
    if prospective_response is not None:
        return prospective_response
    if normalized_method != "GET":
        return _json_response(405, {"error": "method_not_allowed", "research_only": True})

    shell = shell or build_nas_app_shell()
    local_policy = shell["auth_policy"]
    shell_response = dispatch_nas_app_request(
        shell,
        NasAppRequest(
            path=normalized_path,
            method=normalized_method,
            headers={
                local_policy["session_header_name"]: local_policy[
                    "local_smoke_session_marker"
                ],
            },
        ),
    )
    return RuntimeResponse(
        status_code=int(shell_response["status_code"]),
        content_type=str(shell_response["content_type"]),
        body=str(shell_response["body"]),
        route_id=shell_response.get("route_id"),
    )


def main(argv: list[str] | None = None) -> int:
    """Run the private NAS HTTP server."""

    parser = ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("BUSINESS_CYCLE_BIND_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("BUSINESS_CYCLE_BIND_PORT", "8000")),
    )
    args = parser.parse_args(argv)

    cache = NasAppShellTtlCache(
        _build_startup_shell,
        ttl_seconds=_positive_env_int(
            "BUSINESS_CYCLE_DASHBOARD_SHELL_TTL_SECONDS",
            DEFAULT_DASHBOARD_SHELL_TTL_SECONDS,
        ),
    )
    server = ThreadingHTTPServer((args.host, args.port), _RuntimeHandler)
    server.nas_app_shell = cache.get()  # type: ignore[attr-defined]
    server.nas_app_shell_cache = cache  # type: ignore[attr-defined]
    server.login_attempt_limiter = LoginAttemptLimiter.from_environment()  # type: ignore[attr-defined]
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


def _build_startup_shell() -> dict[str, Any]:
    """Use live Postgres when configured; never silently hide a configured failure."""

    if os.environ.get("BUSINESS_CYCLE_DATABASE_URL"):
        return build_nas_live_dashboard_runtime(
            refresh_status_path=os.environ.get("BUSINESS_CYCLE_REFRESH_STATUS_PATH"),
            declared_registry_path=os.environ.get(
                "BUSINESS_CYCLE_DECLARED_CYCLE_STATE_PATH"
            ),
            source_operations_status_path=os.environ.get(
                "BUSINESS_CYCLE_SOURCE_OPERATIONS_STATUS_PATH"
            ),
            release_aware_schedule_status_path=os.environ.get(
                "BUSINESS_CYCLE_RELEASE_AWARE_SCHEDULE_STATUS_PATH"
            ),
            pit_backfill_status_path=os.environ.get(
                "BUSINESS_CYCLE_PIT_BACKFILL_STATUS_PATH"
            ),
            broader_pit_status_path=os.environ.get(
                "BUSINESS_CYCLE_BROADER_PIT_STATUS_PATH"
            ),
            strict_replay_timeline_status_path=os.environ.get(
                "BUSINESS_CYCLE_STRICT_REPLAY_TIMELINE_STATUS_PATH"
            ),
        )["nas_app_shell"]
    return build_nas_app_shell()


class _RuntimeHandler(BaseHTTPRequestHandler):
    server_version = "BusinessCycleNAS/phase127"

    def do_GET(self) -> None:  # noqa: N802
        response = build_runtime_response(
            path=self.path,
            method="GET",
            headers={key: value for key, value in self.headers.items()},
            shell=_server_shell(self.server),
        )
        self._send_runtime_response(response)

    def do_POST(self) -> None:  # noqa: N802
        normalized_path = urlparse(self.path).path or "/"
        limiter = getattr(self.server, "login_attempt_limiter", None)
        if not isinstance(limiter, LoginAttemptLimiter):
            limiter = LoginAttemptLimiter.from_environment()
        client_key = str(self.client_address[0])
        if normalized_path == "/login" and limiter.is_blocked(client_key):
            self._send_runtime_response(
                _login_rate_limited_response(limiter.retry_after_seconds(client_key)),
            )
            return
        content_length = _content_length(self.headers)
        if content_length > MAX_LOGIN_BODY_BYTES:
            self._send_runtime_response(
                _html_response(
                    413,
                    _login_page(error="登入請求過大，請重新整理後再試一次。"),
                ),
            )
            return
        body = self.rfile.read(content_length).decode("utf-8")
        response = build_runtime_response(
            path=self.path,
            method="POST",
            headers={key: value for key, value in self.headers.items()},
            body=body,
        )
        if normalized_path == "/login":
            if response.status_code == 401:
                limiter.record_failure(client_key)
            elif response.status_code == 303:
                limiter.clear(client_key)
        if response.route_id in {
            "nas_declared_phase_start_apply",
            "nas_declared_phase_start_rollback",
        }:
            cache = getattr(self.server, "nas_app_shell_cache", None)
            if isinstance(cache, NasAppShellTtlCache):
                cache.invalidate()
        self._send_runtime_response(response)

    def log_message(self, format: str, *args: object) -> None:
        """Silence default request logging; DSM/container logs stay compact."""

        _ = (format, args)

    def _send_runtime_response(self, response: RuntimeResponse) -> None:
        body = response.body.encode("utf-8")
        self.send_response(response.status_code)
        self.send_header("content-type", response.content_type)
        self.send_header("cache-control", "no-store")
        for key, value in _response_security_headers().items():
            self.send_header(key, value)
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _server_shell(server: Any) -> dict[str, Any] | None:
    cache = getattr(server, "nas_app_shell_cache", None)
    if isinstance(cache, NasAppShellTtlCache):
        return cache.get()
    return getattr(server, "nas_app_shell", None)


def _cycle_state_response(
    *,
    path: str,
    method: str,
    body: str,
    active_registry_path: str,
) -> RuntimeResponse | None:
    operator_paths = {
        "/cycle-state",
        "/api/cycle-state.json",
        "/cycle-state/preview",
        "/cycle-state/apply",
        "/cycle-state/rollback",
    }
    if path not in operator_paths:
        return None
    status = build_nas_declared_phase_start_status(
        active_registry_path=active_registry_path,
    )
    if path == "/cycle-state" and method == "GET":
        return RuntimeResponse(
            200,
            "text/html; charset=utf-8",
            render_nas_declared_phase_start_page(status=status),
            route_id="nas_declared_phase_start_page",
        )
    if path == "/api/cycle-state.json" and method == "GET":
        return RuntimeResponse(
            200,
            "application/json",
            json.dumps(status, sort_keys=True),
            route_id="nas_declared_phase_start_api",
        )
    if method != "POST":
        return _json_response(405, {"error": "method_not_allowed", "research_only": True})
    form = parse_qs(body, keep_blank_values=True)
    try:
        if path == "/cycle-state/preview":
            note = _form_value(form, "confirmation_note")
            preview = preview_nas_declared_phase_start_update(
                exact_start_date=_form_value(form, "exact_start_date") or None,
                window_start_date=_form_value(form, "window_start_date") or None,
                window_end_date=_form_value(form, "window_end_date") or None,
                confirmation_note=note,
                as_of=_form_value(form, "as_of") or None,
                active_registry_path=active_registry_path,
            )
            return RuntimeResponse(
                200 if preview["preview_valid"] else 400,
                "text/html; charset=utf-8",
                render_nas_declared_phase_start_page(
                    status=status,
                    preview=preview,
                    confirmation_note=note,
                ),
                route_id="nas_declared_phase_start_preview",
            )
        if path == "/cycle-state/apply":
            apply_nas_declared_phase_start_update(
                preview_token=_form_value(form, "preview_token"),
                confirmation=_form_value(form, "apply_confirmation"),
                exact_start_date=_form_value(form, "exact_start_date") or None,
                window_start_date=_form_value(form, "window_start_date") or None,
                window_end_date=_form_value(form, "window_end_date") or None,
                confirmation_note=_form_value(form, "confirmation_note"),
                as_of=_form_value(form, "as_of") or None,
                active_registry_path=active_registry_path,
            )
            updated = build_nas_declared_phase_start_status(
                active_registry_path=active_registry_path,
            )
            return RuntimeResponse(
                200,
                "text/html; charset=utf-8",
                render_nas_declared_phase_start_page(
                    status=updated,
                    message_zh="榮景起始資訊已寫入 NAS 私有受治理 registry。",
                ),
                route_id="nas_declared_phase_start_apply",
            )
        rollback_nas_declared_phase_start_update(
            expected_active_hash=_form_value(form, "expected_active_hash"),
            confirmation=_form_value(form, "rollback_confirmation"),
            active_registry_path=active_registry_path,
        )
        rolled_back = build_nas_declared_phase_start_status(
            active_registry_path=active_registry_path,
        )
        return RuntimeResponse(
            200,
            "text/html; charset=utf-8",
            render_nas_declared_phase_start_page(
                status=rolled_back,
                message_zh="已回復上一版 declared boom 起始資訊。",
            ),
            route_id="nas_declared_phase_start_rollback",
        )
    except (NasDeclaredPhaseStartError, ValueError) as exc:
        return RuntimeResponse(
            400,
            "text/html; charset=utf-8",
            render_nas_declared_phase_start_page(
                status=status,
                error_zh=_cycle_state_error_zh(str(exc)),
            ),
            route_id="nas_declared_phase_start_error",
        )


def _source_operations_response(
    *,
    path: str,
    method: str,
    shell: dict[str, Any] | None,
) -> RuntimeResponse | None:
    if path not in {"/source-operations", "/api/source-operations.json"}:
        return None
    if method != "GET":
        return _json_response(405, {"error": "method_not_allowed", "research_only": True})
    diagnostics = (shell or {}).get("source_release_diagnostics")
    if not isinstance(diagnostics, dict):
        return _json_response(
            503,
            {
                "error": "source_operations_not_available",
                "research_only": True,
                "private_nas_only": True,
            },
        )
    if path == "/source-operations":
        return RuntimeResponse(
            200,
            "text/html; charset=utf-8",
            render_nas_source_operations_page(diagnostics),
            route_id="nas_source_operations_page",
        )
    return RuntimeResponse(
        200,
        "application/json",
        build_nas_source_operations_api(diagnostics),
        route_id="nas_source_operations_api",
    )


def _technology_cycle_response(
    *,
    path: str,
    method: str,
    shell: dict[str, Any] | None,
) -> RuntimeResponse | None:
    if path not in {"/technology-cycle", "/api/technology-cycle.json"}:
        return None
    if method != "GET":
        return _json_response(405, {"error": "method_not_allowed", "research_only": True})
    resolved = shell or {}
    view = resolved.get("technology_manufacturing_cycle")
    if not isinstance(view, dict):
        return _json_response(503, {
            "error": "technology_cycle_not_available",
            "research_only": True,
            "private_nas_only": True,
        })
    if path == "/technology-cycle":
        html = resolved.get("technology_manufacturing_cycle_html")
        if not isinstance(html, str) or not html:
            return _json_response(503, {"error": "technology_cycle_renderer_unavailable"})
        return RuntimeResponse(
            200,
            "text/html; charset=utf-8",
            html,
            route_id="technology_manufacturing_cycle_page",
        )
    return RuntimeResponse(
        200,
        "application/json",
        json.dumps(view, sort_keys=True),
        route_id="technology_manufacturing_cycle_api",
    )


def _portfolio_replay_response(
    *,
    path: str,
    method: str,
    shell: dict[str, Any] | None,
) -> RuntimeResponse | None:
    routes = {
        "/portfolio-research",
        "/api/portfolio-research.json",
        "/historical-replay",
        "/api/historical-replay.json",
    }
    if path not in routes:
        return None
    if method != "GET":
        return _json_response(405, {"error": "method_not_allowed", "research_only": True})
    resolved = shell or {}
    lab = resolved.get("portfolio_replay_lab")
    if not isinstance(lab, dict):
        return _json_response(
            503,
            {
                "error": "portfolio_replay_lab_not_available",
                "research_only": True,
                "private_nas_only": True,
            },
        )
    if path == "/portfolio-research":
        html_page = resolved.get("portfolio_research_html")
        if not isinstance(html_page, str) or not html_page:
            return _json_response(503, {"error": "portfolio_renderer_unavailable"})
        return RuntimeResponse(
            200,
            "text/html; charset=utf-8",
            html_page,
            route_id="nas_portfolio_research_page",
        )
    if path == "/historical-replay":
        html_page = resolved.get("historical_replay_html")
        if not isinstance(html_page, str) or not html_page:
            return _json_response(503, {"error": "historical_replay_renderer_unavailable"})
        return RuntimeResponse(
            200,
            "text/html; charset=utf-8",
            html_page,
            route_id="nas_historical_replay_page",
        )
    view = (
        lab["portfolio_research"]
        if path == "/api/portfolio-research.json"
        else lab["historical_replay"]
    )
    return RuntimeResponse(
        200,
        "application/json",
        json.dumps(view, sort_keys=True),
        route_id=(
            "nas_portfolio_research_api"
            if path == "/api/portfolio-research.json"
            else "nas_historical_replay_api"
        ),
    )


def _prospective_validation_response(
    *,
    path: str,
    method: str,
    shell: dict[str, Any] | None,
) -> RuntimeResponse | None:
    if path not in {
        "/prospective-monitoring",
        "/api/prospective-monitoring.json",
    }:
        return None
    if method != "GET":
        return _json_response(405, {"error": "method_not_allowed", "research_only": True})
    resolved = shell or {}
    state = resolved.get("prospective_validation_wait_state")
    if not isinstance(state, dict):
        return _json_response(
            503,
            {
                "error": "prospective_wait_state_not_available",
                "research_only": True,
                "private_nas_only": True,
            },
        )
    if path == "/prospective-monitoring":
        html_page = resolved.get("prospective_validation_html")
        if not isinstance(html_page, str) or not html_page:
            return _json_response(503, {"error": "prospective_renderer_unavailable"})
        return RuntimeResponse(
            200,
            "text/html; charset=utf-8",
            html_page,
            route_id="nas_prospective_validation_page",
        )
    return RuntimeResponse(
        200,
        "application/json",
        json.dumps(state, sort_keys=True),
        route_id="nas_prospective_validation_api",
    )


def _form_value(form: dict[str, list[str]], key: str) -> str:
    return form.get(key, [""])[0].strip()


def _cycle_state_error_zh(message: str) -> str:
    translations = {
        "explicit apply confirmation is required": "請勾選明確套用確認。",
        "confirmation note is required": "請填寫確認理由。",
        "declared phase-start preview is invalid": "起始日或區間未通過預覽驗證。",
        "stale or mismatched preview token": "預覽已過期或內容不一致，請重新預覽。",
        "active registry changed after preview": "Registry 已變更，請重新預覽。",
        "explicit rollback confirmation is required": "請勾選 rollback 確認。",
        "private NAS registry override does not exist": "目前沒有可 rollback 的 NAS override。",
        "active registry hash changed before rollback": "Registry 已變更，請重新載入頁面。",
        "no declared phase-start backup is available": "找不到可用的 registry 備份。",
    }
    return translations.get(message, "輸入未通過安全驗證，請重新檢查。")


def _json_response(status_code: int, payload: dict[str, Any]) -> RuntimeResponse:
    return RuntimeResponse(
        status_code=status_code,
        content_type="application/json",
        body=json.dumps(payload, sort_keys=True),
    )


def _html_response(
    status_code: int,
    body: str,
    *,
    headers: dict[str, str] | None = None,
) -> RuntimeResponse:
    return RuntimeResponse(
        status_code=status_code,
        content_type="text/html; charset=utf-8",
        body=body,
        headers=headers or {},
    )


def _redirect_response(
    location: str,
    *,
    extra_headers: dict[str, str] | None = None,
) -> RuntimeResponse:
    headers = {"Location": location}
    headers.update(extra_headers or {})
    return RuntimeResponse(
        status_code=303,
        content_type="text/plain; charset=utf-8",
        body="redirect",
        headers=headers,
    )


def _login_rate_limited_response(retry_after_seconds: int) -> RuntimeResponse:
    return _html_response(
        429,
        _login_page(error="登入嘗試過多，請稍後再試。"),
        headers={"Retry-After": str(retry_after_seconds)},
    )


def _login_response(
    *,
    method: str,
    body: str,
    headers: dict[str, str],
    session_secret: str | None,
) -> RuntimeResponse:
    secret = session_secret if session_secret is not None else _session_secret()
    private_lan_http = _private_lan_http_request(headers)
    if method.upper() == "GET":
        return _html_response(
            200,
            _login_page(private_lan_http=private_lan_http),
        )
    if method.upper() != "POST":
        return _json_response(405, {"error": "method_not_allowed", "research_only": True})
    if not secret:
        return _json_response(
            503,
            {
                "error": "session_secret_not_configured",
                "research_only": True,
                "private_nas_only": True,
            },
        )
    submitted = parse_qs(body, keep_blank_values=True).get("session_secret", [""])[0]
    if not hmac.compare_digest(submitted, secret):
        return _html_response(
            401,
            _login_page(
                error="登入密碼不正確，請再試一次。",
                private_lan_http=private_lan_http,
            ),
        )
    token = _session_token(secret)
    return _redirect_response(
        "/",
        extra_headers={
            "Set-Cookie": _session_cookie(
                token,
                max_age=604800,
                secure=_secure_cookie_for_request(headers),
            ),
        },
    )


def _login_page(error: str = "", *, private_lan_http: bool = False) -> str:
    error_html = (
        f'<p class="error">{html.escape(error)}</p>'
        if error
        else ""
    )
    transport_html = (
        '<p class="transport">目前使用家中私有 LAN HTTP。此入口可登入，'
        "但離家使用時請改用 Tailscale HTTPS。</p>"
        if private_lan_http
        else ""
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>景氣循環研究服務登入</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f5f7fa;
      color: #172033;
    }}
    main {{
      width: min(92vw, 420px);
      padding: 28px;
      border: 1px solid #d9e0ea;
      border-radius: 8px;
      background: #fff;
      box-shadow: 0 18px 50px rgba(23, 32, 51, .08);
    }}
    h1 {{ margin: 0 0 8px; font-size: 24px; }}
    p {{ margin: 0 0 18px; line-height: 1.55; color: #536070; }}
    label {{ display: block; margin-bottom: 8px; font-weight: 650; }}
    input {{
      width: 100%;
      box-sizing: border-box;
      padding: 12px;
      border: 1px solid #b9c4d0;
      border-radius: 6px;
      font-size: 16px;
    }}
    button {{
      width: 100%;
      margin-top: 16px;
      padding: 12px;
      border: 0;
      border-radius: 6px;
      background: #1d4ed8;
      color: #fff;
      font-size: 16px;
      font-weight: 700;
    }}
    button:disabled {{ opacity: .7; cursor: wait; }}
    .error {{ color: #b42318; font-weight: 650; }}
    .transport {{
      padding: 10px 12px;
      border-left: 3px solid #2563eb;
      background: #eff6ff;
      color: #1e3a5f;
      font-size: 14px;
    }}
    .caveat {{ margin-top: 18px; font-size: 13px; color: #667085; }}
  </style>
</head>
<body>
  <main>
    <h1>景氣循環研究服務</h1>
    <p>這是私人 NAS 研究儀表板。請輸入你在 Container Manager 設定的服務密碼。</p>
    {transport_html}
    {error_html}
    <form method="post" action="/login">
      <label for="session_secret">服務密碼</label>
      <input id="session_secret" name="session_secret" type="password" autocomplete="current-password" required>
      <button id="login-submit" type="submit">進入研究儀表板</button>
    </form>
    <p class="caveat">研究用途；不提供個人化交易指令、買賣訊號或保證績效。</p>
  </main>
  <script>
    document.querySelector("form").addEventListener("submit", () => {{
      const button = document.getElementById("login-submit");
      button.disabled = true;
      button.textContent = "登入中...";
    }});
  </script>
</body>
</html>"""


def _session_secret() -> str:
    return os.environ.get("BUSINESS_CYCLE_APP_SESSION_SECRET", "")


def _session_header_name() -> str:
    return os.environ.get("BUSINESS_CYCLE_APP_SESSION_HEADER", DEFAULT_SESSION_HEADER)


def _session_cookie(
    value: str,
    *,
    max_age: int,
    secure: bool | None = None,
) -> str:
    attributes = [
        f"{SESSION_COOKIE_NAME}={value}",
        "Path=/",
        f"Max-Age={max_age}",
        "HttpOnly",
        "SameSite=Strict",
    ]
    if _secure_cookie_enabled() if secure is None else secure:
        attributes.append("Secure")
    return "; ".join(attributes)


def _secure_cookie_enabled() -> bool:
    return _env_flag("BUSINESS_CYCLE_APP_SECURE_COOKIE", default=False)


def _secure_cookie_for_request(headers: dict[str, str]) -> bool:
    forwarded_proto = headers.get("x-forwarded-proto", "").split(",", 1)[0].strip()
    if forwarded_proto.lower() == "https":
        return True
    if _private_lan_http_request(headers):
        return False
    return _secure_cookie_enabled()


def _private_lan_http_request(headers: dict[str, str]) -> bool:
    if not _env_flag("BUSINESS_CYCLE_PRIVATE_LAN_HTTP_COOKIE_ALLOWED", default=False):
        return False
    forwarded_proto = headers.get("x-forwarded-proto", "").split(",", 1)[0].strip()
    if forwarded_proto.lower() == "https":
        return False
    host = headers.get("host", "").strip().lower()
    allowed_hosts = {
        value.strip().lower()
        for value in os.environ.get("BUSINESS_CYCLE_PRIVATE_LAN_HOSTS", "").split(",")
        if value.strip()
    }
    return bool(host and host in allowed_hosts)


def _response_security_headers() -> dict[str, str]:
    headers = {
        "Content-Security-Policy": (
            "default-src 'self'; base-uri 'none'; form-action 'self'; "
            "frame-ancestors 'none'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'"
        ),
        "Referrer-Policy": "no-referrer",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
    }
    if _secure_cookie_enabled():
        headers["Strict-Transport-Security"] = "max-age=31536000"
    return headers


def _normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    normalized = dict(headers)
    for key, value in headers.items():
        normalized[key.lower()] = value
    return normalized


def _authorized(headers: dict[str, str], secret: str) -> bool:
    header_name = _session_header_name()
    return (
        headers.get(header_name) == secret
        or headers.get(header_name.lower()) == secret
        or _cookie_value(headers, SESSION_COOKIE_NAME) == _session_token(secret)
    )


def _session_token(secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        b"business_cycle_private_nas_session_v1",
        hashlib.sha256,
    ).hexdigest()


def _cookie_value(headers: dict[str, str], name: str) -> str | None:
    cookie = headers.get("cookie") or headers.get("Cookie") or ""
    for part in cookie.split(";"):
        key, _, value = part.strip().partition("=")
        if key == name:
            return value
    return None


def _prefers_html(headers: dict[str, str]) -> bool:
    accept = headers.get("accept") or headers.get("Accept") or ""
    return "text/html" in accept


def _content_length(headers: Any) -> int:
    value = headers.get("Content-Length", "0")
    try:
        return max(0, int(value))
    except ValueError:
        return 0


def _positive_env_int(name: str, default: int) -> int:
    value = os.environ.get(name, "")
    try:
        parsed = int(value) if value else default
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _env_flag(name: str, *, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    raise SystemExit(main())
