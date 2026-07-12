from __future__ import annotations

import re
from urllib.parse import urlencode

import pytest

from business_cycle.service import nas_runtime_server
from business_cycle.service.healthcheck import build_healthcheck_summary
from business_cycle.service.nas_runtime_server import (
    LoginAttemptLimiter,
    NasAppShellTtlCache,
    build_runtime_response,
)
from business_cycle.service.nas_official_release_calendar import (
    build_nas_official_release_diagnostics,
)
from business_cycle.service.refresh_worker_disabled_until_gate import main as refresh_main
from business_cycle.storage.nas_postgres_live_revised_import import (
    load_nas_postgres_live_revised_import_contract,
)

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
                "release_family_count": 12,
                "nas_v1_operational_acceptance_status": (
                    "accepted_private_nas_v1_research_service"
                ),
                "nas_v1_operational_acceptance_passed": True,
                "prospective_wait_state": "awaiting_canonical_as_of",
                "prospective_protocol_started": False,
                "prospective_registry_record_count": 0,
                "real_registry_write_attempt_count": 0,
                "prospective_validation_seal_ready": False,
                "nas_page_scan_ready": True,
                "nas_scanned_page_count": 8,
                "nas_unfinished_marker_count": 0,
                "nas_software_placeholder_gap_count": 0,
                "nas_disclosed_gap_page_count": 8,
            },
        },
    )
    assert '"live_db_connected": true' in live_ready.body
    assert '"dashboard_data_source": "live_postgres_read_only"' in live_ready.body
    assert '"source_operations_route_count": 2' in live_ready.body
    assert '"release_family_count": 12' in live_ready.body
    assert '"nas_v1_operational_acceptance_passed": true' in live_ready.body
    assert '"prospective_wait_state": "awaiting_canonical_as_of"' in live_ready.body
    assert '"prospective_registry_record_count": 0' in live_ready.body
    assert '"nas_page_scan_ready": true' in live_ready.body
    assert '"nas_scanned_page_count": 8' in live_ready.body
    assert '"nas_software_placeholder_gap_count": 0' in live_ready.body
    assert '"nas_disclosed_gap_page_count": 8' in live_ready.body


def test_runtime_prospective_wait_routes_are_private_metadata_only() -> None:
    state = {
        "current_wait_state": "awaiting_canonical_as_of",
        "protocol_started": False,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    shell = {
        "prospective_validation_wait_state": state,
        "prospective_validation_html": "<html lang=\"zh-Hant-TW\">前瞻驗證進度</html>",
    }
    secret = "expected-secret"
    unauthorized = build_runtime_response(
        path="/prospective-monitoring",
        session_secret=secret,
        headers={"Accept": "text/html"},
        shell=shell,
    )
    page = build_runtime_response(
        path="/prospective-monitoring",
        session_secret=secret,
        headers={"X-Business-Cycle-Session": secret},
        shell=shell,
    )
    api = build_runtime_response(
        path="/api/prospective-monitoring.json",
        session_secret=secret,
        headers={"X-Business-Cycle-Session": secret},
        shell=shell,
    )

    assert unauthorized.status_code == 303
    assert page.status_code == 200
    assert "前瞻驗證進度" in page.body
    assert api.status_code == 200
    assert '"protocol_started": false' in api.body
    assert '"prospective_registry_record_count": 0' in api.body


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
        lambda **_: {"nas_app_shell": shell},
    )

    assert nas_runtime_server._build_startup_shell() is shell  # noqa: SLF001


def test_runtime_ttl_cache_refreshes_and_retains_visible_last_good_snapshot() -> None:
    now = [100.0]
    builds = [
        {"route_count": 5, "trust_metadata": {"refresh_state": "scheduled"}},
        {"route_count": 5, "trust_metadata": {"refresh_state": "succeeded"}},
    ]

    def builder() -> dict[str, object]:
        if builds:
            return builds.pop(0)
        raise RuntimeError("database temporarily unavailable")

    cache = NasAppShellTtlCache(builder, ttl_seconds=10, clock=lambda: now[0])
    assert cache.get()["trust_metadata"]["refresh_state"] == "scheduled"
    now[0] = 111.0
    assert cache.get()["trust_metadata"]["refresh_state"] == "succeeded"
    assert cache.refresh_count == 2

    now[0] = 122.0
    stale = cache.get()
    assert stale["trust_metadata"]["dashboard_snapshot_status"] == (
        "stale_after_refresh_error"
    )
    assert cache.refresh_error_count == 1
    assert "database temporarily unavailable" not in str(stale)


def test_runtime_declared_start_routes_require_auth_preview_apply_and_rollback(
    tmp_path,
) -> None:
    active = tmp_path / "declared_cycle_state_registry.yaml"
    secret = "expected-secret"
    auth = {"X-Business-Cycle-Session": secret}
    unauthorized = build_runtime_response(
        path="/cycle-state",
        session_secret=secret,
        headers={"Accept": "text/html"},
        cycle_state_registry_path=str(active),
    )
    page = build_runtime_response(
        path="/cycle-state",
        session_secret=secret,
        headers=auth,
        cycle_state_registry_path=str(active),
    )
    preview = build_runtime_response(
        path="/cycle-state/preview",
        method="POST",
        session_secret=secret,
        headers=auth,
        body=urlencode(
            {
                "exact_start_date": "2025-06-01",
                "confirmation_note": "user confirmed exact date",
                "as_of": "2026-07-10",
            },
        ),
        cycle_state_registry_path=str(active),
    )
    token = re.search(r'name="preview_token" value="([a-f0-9]+)"', preview.body)
    assert token is not None
    applied = build_runtime_response(
        path="/cycle-state/apply",
        method="POST",
        session_secret=secret,
        headers=auth,
        body=urlencode(
            {
                "preview_token": token.group(1),
                "exact_start_date": "2025-06-01",
                "confirmation_note": "user confirmed exact date",
                "as_of": "2026-07-10",
                "apply_confirmation": "CONFIRM_DECLARED_BOOM_START_CONTEXT",
            },
        ),
        cycle_state_registry_path=str(active),
    )
    api = build_runtime_response(
        path="/api/cycle-state.json",
        session_secret=secret,
        headers=auth,
        cycle_state_registry_path=str(active),
    )
    active_hash = __import__("json").loads(api.body)["active_registry_hash"]
    rollback = build_runtime_response(
        path="/cycle-state/rollback",
        method="POST",
        session_secret=secret,
        headers=auth,
        body=urlencode(
            {
                "expected_active_hash": active_hash,
                "rollback_confirmation": "CONFIRM_DECLARED_BOOM_START_ROLLBACK",
            },
        ),
        cycle_state_registry_path=str(active),
    )

    assert unauthorized.status_code == 303
    assert page.status_code == 200
    assert "景氣狀態設定" in page.body
    assert "尚待使用者確認" in page.body
    assert preview.status_code == 200
    assert "寫入前預覽" in preview.body
    assert applied.status_code == 200
    assert applied.route_id == "nas_declared_phase_start_apply"
    assert "已寫入 NAS 私有受治理 registry" in applied.body
    assert '"declared_phase_start_context_status": "confirmed_exact_date"' in api.body
    assert rollback.status_code == 200
    assert rollback.route_id == "nas_declared_phase_start_rollback"
    assert "已回復上一版" in rollback.body


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

    monkeypatch.setenv("BUSINESS_CYCLE_PRIVATE_LAN_HTTP_COOKIE_ALLOWED", "true")
    monkeypatch.setenv(
        "BUSINESS_CYCLE_PRIVATE_LAN_HOSTS",
        "192.168.1.116,192.168.1.116:18080",
    )
    lan_login_page = build_runtime_response(
        path="/login",
        method="GET",
        headers={"Host": "192.168.1.116:18080"},
    )
    lan_login = build_runtime_response(
        path="/login",
        method="POST",
        headers={"Host": "192.168.1.116:18080"},
        session_secret="expected-secret",
        body="session_secret=expected-secret",
    )
    tailscale_login = build_runtime_response(
        path="/login",
        method="POST",
        headers={
            "Host": "mao-family-nas.tailb97dc1.ts.net",
            "X-Forwarded-Proto": "https",
        },
        session_secret="expected-secret",
        body="session_secret=expected-secret",
    )

    assert "家中私有 LAN HTTP" in lan_login_page.body
    assert "Secure" not in lan_login.headers["Set-Cookie"]
    assert "Secure" in tailscale_login.headers["Set-Cookie"]


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


def test_phase115_source_operations_routes_are_private_and_traditional_chinese() -> None:
    series_ids = load_nas_postgres_live_revised_import_contract()[
        "source_policy"
    ]["direct_series_ids"]
    diagnostics = build_nas_official_release_diagnostics(
        as_of="2026-07-10",
        series_inputs=[
            {
                "series_id": series_id,
                "frequency": "monthly",
                "latest_observation_date": "2026-07-01",
                "freshness_status": "fresh",
            }
            for series_id in series_ids
        ],
        refresh_status={
            "refresh_state": "succeeded",
            "last_run_state": "succeeded",
            "last_completed_at_utc": "2026-07-10T12:00:00Z",
            "series_refresh_results": [],
        },
    )
    shell = {"source_release_diagnostics": diagnostics}
    unauthorized = build_runtime_response(
        path="/source-operations",
        session_secret="expected-secret",
        shell=shell,
    )
    page = build_runtime_response(
        path="/source-operations",
        session_secret="expected-secret",
        headers={"X-Business-Cycle-Session": "expected-secret"},
        shell=shell,
    )
    api = build_runtime_response(
        path="/api/source-operations.json",
        session_secret="expected-secret",
        headers={"X-Business-Cycle-Session": "expected-secret"},
        shell=shell,
    )

    assert unauthorized.status_code == 401
    assert page.status_code == 200
    assert page.route_id == "nas_source_operations_page"
    assert "官方資料發布與更新維運" in page.body
    assert "逐序列 refresh drilldown" in page.body
    assert "不會冒充官方延遲" in page.body
    assert "受治理重試與備份還原" in page.body
    assert "私有 NAS 備份還原演練" in page.body
    assert "固定時間與官方發布補抓" in page.body
    assert "03:30" in page.body
    assert "私人備份保留預覽" in page.body
    assert "私人 NAS v1.0 操作驗收" in page.body
    assert "不代表模型已完成經濟或前瞻驗證" in page.body
    assert "歷史資料模式完整度" in page.body
    assert "PIT 只代表 ALFRED realtime interval 已保存" in page.body
    assert api.status_code == 200
    assert api.route_id == "nas_source_operations_api"
    assert '"release_family_count": 12' in api.body
    assert '"candidate_phase_emitted": false' in api.body


def test_healthcheck_import_mode_passes() -> None:
    summary = build_healthcheck_summary(url=None)

    assert summary["healthcheck_ready"] is True
    assert summary["status"] == "ok"


def test_disabled_refresh_worker_exits_successfully(capsys: pytest.CaptureFixture[str]) -> None:
    assert refresh_main() == 0
    output = capsys.readouterr().out
    assert '"refresh_worker_enabled": false' in output
    assert '"live_fetch_attempt_count": 0' in output


def test_phase122_technology_cycle_routes_are_private_research_only() -> None:
    view = {
        "view_model_id": "technology_manufacturing_cycle_research_v1",
        "research_only": True,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    shell = {
        "technology_manufacturing_cycle": view,
        "technology_manufacturing_cycle_html": "<h1>台美科技製造循環</h1>",
    }
    unauthorized = build_runtime_response(
        path="/technology-cycle",
        session_secret="expected-secret",
        shell=shell,
    )
    page = build_runtime_response(
        path="/technology-cycle",
        session_secret="expected-secret",
        headers={"X-Business-Cycle-Session": "expected-secret"},
        shell=shell,
    )
    api = build_runtime_response(
        path="/api/technology-cycle.json",
        session_secret="expected-secret",
        headers={"X-Business-Cycle-Session": "expected-secret"},
        shell=shell,
    )

    assert unauthorized.status_code == 401
    assert page.status_code == 200
    assert page.route_id == "technology_manufacturing_cycle_page"
    assert "台美科技製造循環" in page.body
    assert api.status_code == 200
    assert api.route_id == "technology_manufacturing_cycle_api"
    assert '"candidate_phase_emitted": false' in api.body


def test_phase124_portfolio_and_replay_routes_are_private_and_research_only() -> None:
    shell = {
        "portfolio_replay_lab": {
            "portfolio_research": {"research_only": True, "template_cards": []},
            "historical_replay": {"research_only": True, "scenario_rows": []},
        },
        "portfolio_research_html": "<h1>景氣循環配置研究</h1>",
        "historical_replay_html": "<h1>景氣循環歷史重播</h1>",
    }
    headers = {"X-Business-Cycle-Session": "expected-secret"}

    unauthorized = build_runtime_response(
        path="/portfolio-research",
        session_secret="expected-secret",
        shell=shell,
    )
    portfolio = build_runtime_response(
        path="/portfolio-research",
        session_secret="expected-secret",
        headers=headers,
        shell=shell,
    )
    replay = build_runtime_response(
        path="/historical-replay",
        session_secret="expected-secret",
        headers=headers,
        shell=shell,
    )
    portfolio_api = build_runtime_response(
        path="/api/portfolio-research.json",
        session_secret="expected-secret",
        headers=headers,
        shell=shell,
    )
    replay_api = build_runtime_response(
        path="/api/historical-replay.json",
        session_secret="expected-secret",
        headers=headers,
        shell=shell,
    )

    assert unauthorized.status_code == 401
    assert portfolio.status_code == replay.status_code == 200
    assert portfolio.route_id == "nas_portfolio_research_page"
    assert replay.route_id == "nas_historical_replay_page"
    assert portfolio_api.route_id == "nas_portfolio_research_api"
    assert replay_api.route_id == "nas_historical_replay_api"
    assert '"research_only": true' in portfolio_api.body
    assert '"research_only": true' in replay_api.body
