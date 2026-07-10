from __future__ import annotations

import pytest

from business_cycle.service import nas_runtime_server
from business_cycle.service.healthcheck import build_healthcheck_summary
from business_cycle.service.nas_runtime_server import (
    LoginAttemptLimiter,
    build_runtime_response,
)
from business_cycle.service.refresh_worker_disabled_until_gate import main as refresh_main

pytestmark = pytest.mark.archive_regression


def test_runtime_health_and_ready_endpoints_do_not_require_secret() -> None:
    health = build_runtime_response(path="/healthz")
    ready = build_runtime_response(path="/readyz")

    assert health.status_code == 200
    assert "business_cycle_private_nas" in health.body
    assert ready.status_code == 200
    assert "route_count" in ready.body

    live_ready = build_runtime_response(
        path="/readyz",
        shell={
            "route_count": 5,
            "trust_metadata": {
                "dashboard_data_source": "live_postgres_read_only",
                "live_db_connected": True,
                "snapshot_as_of": "2026-07-10",
                "database_latest_observation_date": "2026-07-04",
            },
        },
    )
    assert '"live_db_connected": true' in live_ready.body
    assert '"dashboard_data_source": "live_postgres_read_only"' in live_ready.body


def test_runtime_protected_routes_require_secret() -> None:
    missing_secret = build_runtime_response(path="/", session_secret="")
    wrong_secret = build_runtime_response(
        path="/",
        session_secret="expected-secret",
        headers={"X-Business-Cycle-Session": "wrong"},
    )
    authenticated = build_runtime_response(
        path="/",
        session_secret="expected-secret",
        headers={"X-Business-Cycle-Session": "expected-secret"},
    )

    assert missing_secret.status_code == 503
    assert wrong_secret.status_code == 401
    assert authenticated.status_code == 200
    assert authenticated.content_type.startswith("text/html")


def test_runtime_browser_login_sets_private_session_cookie() -> None:
    login_page = build_runtime_response(path="/login", method="GET")
    bad_login = build_runtime_response(
        path="/login",
        method="POST",
        session_secret="expected-secret",
        body="session_secret=wrong",
    )
    good_login = build_runtime_response(
        path="/login",
        method="POST",
        session_secret="expected-secret",
        body="session_secret=expected-secret",
    )
    cookie = good_login.headers["Set-Cookie"].split(";", maxsplit=1)[0]
    authenticated = build_runtime_response(
        path="/",
        session_secret="expected-secret",
        headers={"Cookie": cookie},
    )

    assert login_page.status_code == 200
    assert "景氣循環研究服務" in login_page.body
    assert bad_login.status_code == 401
    assert good_login.status_code == 303
    assert good_login.headers["Location"] == "/"
    assert "expected-secret" not in good_login.headers["Set-Cookie"]
    assert authenticated.status_code == 200


def test_runtime_browser_without_session_redirects_to_login() -> None:
    response = build_runtime_response(
        path="/",
        session_secret="expected-secret",
        headers={"Accept": "text/html"},
    )

    assert response.status_code == 303
    assert response.headers["Location"] == "/login"


def test_runtime_main_prebuilds_dashboard_shell_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shell = {"route_count": 5}
    events: list[str] = []

    class FakeServer:
        nas_app_shell: dict[str, object]
        login_attempt_limiter: LoginAttemptLimiter

        def __init__(self, address: tuple[str, int], handler: object) -> None:
            assert address == ("127.0.0.1", 8000)
            assert handler is nas_runtime_server._RuntimeHandler  # noqa: SLF001

        def serve_forever(self) -> None:
            assert self.nas_app_shell is shell
            assert isinstance(self.login_attempt_limiter, LoginAttemptLimiter)
            events.append("served")

        def server_close(self) -> None:
            events.append("closed")

    monkeypatch.setattr(nas_runtime_server, "build_nas_app_shell", lambda: shell)
    monkeypatch.setattr(nas_runtime_server, "ThreadingHTTPServer", FakeServer)
    monkeypatch.delenv("BUSINESS_CYCLE_DATABASE_URL", raising=False)

    assert nas_runtime_server.main([]) == 0
    assert events == ["served", "closed"]


def test_runtime_uses_live_postgres_when_database_is_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shell = {"route_count": 5, "trust_metadata": {"live_db_connected": True}}
    monkeypatch.setenv(
        "BUSINESS_CYCLE_DATABASE_URL",
        "postgresql://app:secret@macro_postgres:5432/business_cycle",
    )
    monkeypatch.setattr(
        nas_runtime_server,
        "build_nas_live_dashboard_runtime",
        lambda: {"nas_app_shell": shell},
    )

    assert nas_runtime_server._build_startup_shell() is shell  # noqa: SLF001


def test_runtime_secure_cookie_and_security_headers_follow_https_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BUSINESS_CYCLE_APP_SECURE_COOKIE", "true")

    response = build_runtime_response(
        path="/login",
        method="POST",
        session_secret="expected-secret",
        body="session_secret=expected-secret",
    )
    headers = nas_runtime_server._response_security_headers()  # noqa: SLF001

    assert "Secure" in response.headers["Set-Cookie"]
    assert headers["Strict-Transport-Security"] == "max-age=31536000"
    assert headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]


def test_login_attempt_limiter_blocks_then_expires_without_storing_secret() -> None:
    now = [100.0]
    limiter = LoginAttemptLimiter(
        max_failures=2,
        window_seconds=60,
        clock=lambda: now[0],
    )

    limiter.record_failure("client-a")
    assert limiter.is_blocked("client-a") is False
    limiter.record_failure("client-a")
    assert limiter.is_blocked("client-a") is True
    assert limiter.retry_after_seconds("client-a") == 61

    now[0] = 161.0
    assert limiter.is_blocked("client-a") is False
    assert limiter.retry_after_seconds("client-a") == 0


def test_runtime_rejects_unsupported_method() -> None:
    response = build_runtime_response(
        path="/",
        method="POST",
        session_secret="expected-secret",
        headers={"X-Business-Cycle-Session": "expected-secret"},
    )

    assert response.status_code == 405


def test_healthcheck_import_mode_passes() -> None:
    summary = build_healthcheck_summary(url=None)

    assert summary["healthcheck_ready"] is True
    assert summary["status"] == "ok"


def test_disabled_refresh_worker_exits_successfully(capsys: pytest.CaptureFixture[str]) -> None:
    assert refresh_main() == 0
    output = capsys.readouterr().out
    assert '"refresh_worker_enabled": false' in output
    assert '"live_fetch_attempt_count": 0' in output
