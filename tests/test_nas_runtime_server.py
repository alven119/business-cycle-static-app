from __future__ import annotations

import pytest

from business_cycle.service.healthcheck import build_healthcheck_summary
from business_cycle.service.nas_runtime_server import build_runtime_response
from business_cycle.service.refresh_worker_disabled_until_gate import main as refresh_main

pytestmark = pytest.mark.archive_regression


def test_runtime_health_and_ready_endpoints_do_not_require_secret() -> None:
    health = build_runtime_response(path="/healthz")
    ready = build_runtime_response(path="/readyz")

    assert health.status_code == 200
    assert "business_cycle_private_nas" in health.body
    assert ready.status_code == 200
    assert "route_count" in ready.body


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
