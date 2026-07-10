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
) -> RuntimeResponse:
    """Return a private NAS runtime response without binding a network port."""

    normalized_path = urlparse(path).path or "/"
    headers = _normalize_headers(headers or {})
    if normalized_path == "/login":
        return _login_response(method=method, body=body, session_secret=session_secret)
    if normalized_path == "/logout":
        return _redirect_response(
            "/login",
            extra_headers={
                "Set-Cookie": _session_cookie("", max_age=0),
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
                "research_only": True,
                "public_exposure": False,
            },
        )
    if method.upper() != "GET":
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

    shell = shell or build_nas_app_shell()
    local_policy = shell["auth_policy"]
    shell_response = dispatch_nas_app_request(
        shell,
        NasAppRequest(
            path=normalized_path,
            method=method.upper(),
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

    # The governed dashboard bundle is deterministic but relatively expensive to
    # assemble on the NAS. Build it once so browser requests only dispatch routes.
    shell = _build_startup_shell()
    server = ThreadingHTTPServer((args.host, args.port), _RuntimeHandler)
    server.nas_app_shell = shell  # type: ignore[attr-defined]
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
        return build_nas_live_dashboard_runtime()["nas_app_shell"]
    return build_nas_app_shell()


class _RuntimeHandler(BaseHTTPRequestHandler):
    server_version = "BusinessCycleNAS/phase111"

    def do_GET(self) -> None:  # noqa: N802
        response = build_runtime_response(
            path=self.path,
            method="GET",
            headers={key: value for key, value in self.headers.items()},
            shell=getattr(self.server, "nas_app_shell", None),
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
    session_secret: str | None,
) -> RuntimeResponse:
    secret = session_secret if session_secret is not None else _session_secret()
    if method.upper() == "GET":
        return _html_response(200, _login_page())
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
        return _html_response(401, _login_page(error="登入密碼不正確，請再試一次。"))
    token = _session_token(secret)
    return _redirect_response(
        "/",
        extra_headers={
            "Set-Cookie": _session_cookie(token, max_age=604800),
        },
    )


def _login_page(error: str = "") -> str:
    error_html = (
        f'<p class="error">{html.escape(error)}</p>'
        if error
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
    .caveat {{ margin-top: 18px; font-size: 13px; color: #667085; }}
  </style>
</head>
<body>
  <main>
    <h1>景氣循環研究服務</h1>
    <p>這是私人 NAS 研究儀表板。請輸入你在 Container Manager 設定的服務密碼。</p>
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


def _session_cookie(value: str, *, max_age: int) -> str:
    attributes = [
        f"{SESSION_COOKIE_NAME}={value}",
        "Path=/",
        f"Max-Age={max_age}",
        "HttpOnly",
        "SameSite=Strict",
    ]
    if _secure_cookie_enabled():
        attributes.append("Secure")
    return "; ".join(attributes)


def _secure_cookie_enabled() -> bool:
    return _env_flag("BUSINESS_CYCLE_APP_SECURE_COOKIE", default=False)


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
