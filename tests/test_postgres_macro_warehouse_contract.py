from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from business_cycle.audits.phase110_nas_postgres_live_revised_import_closure import (
    summarize_phase110_nas_postgres_live_revised_import_closure,
)
from business_cycle.audits.phase111_nas_live_postgres_dashboard_closure import (
    summarize_phase111_nas_live_postgres_dashboard_closure,
)
from business_cycle.audits.phase112_nas_scheduled_revised_refresh_closure import (
    summarize_phase112_nas_scheduled_revised_refresh_closure,
)
from business_cycle.audits.phase114_nas_official_release_operations_closure import (
    summarize_phase114_nas_official_release_operations_closure,
)
from business_cycle.audits.phase115_nas_source_retry_restore_closure import (
    summarize_phase115_nas_source_retry_restore_closure,
)
from business_cycle.audits.phase116_nas_release_aware_refresh_closure import (
    summarize_phase116_nas_release_aware_refresh_closure,
)
from business_cycle.audits.phase117_transition_pit_backfill_closure import (
    summarize_phase117_transition_pit_backfill_closure,
)
from business_cycle.audits.phase118_broader_pit_release_replay_closure import (
    summarize_phase118_broader_pit_release_replay_closure,
)
from business_cycle.audits.phase119_private_login_strict_replay_ux_closure import (
    summarize_phase119_private_login_strict_replay_ux_closure,
)
from business_cycle.data_sources import SeriesObservation
from business_cycle.data_sources.alfred_provider import AlfredObservation
from business_cycle.service.nas_live_dashboard import build_nas_live_dashboard_runtime
from business_cycle.service.nas_official_release_calendar import (
    build_nas_official_release_diagnostics,
    summarize_nas_official_release_calendar_contract,
)
from business_cycle.service.nas_release_aware_refresh import (
    ReleaseAwareRefreshError,
    build_backup_retention_preview,
    build_release_aware_schedule_preview,
    load_release_aware_schedule_status,
    serve_release_aware_schedule,
    summarize_nas_release_aware_refresh_contract,
)
from business_cycle.service.nas_scheduled_revised_refresh import (
    _exclusive_refresh_lock,
    run_scheduled_refresh_once,
    serve_refresh_schedule,
    summarize_nas_scheduled_revised_refresh_contract,
)
from business_cycle.service.nas_source_retry_restore import (
    BACKUP_RESTORE_CONFIRMATION,
    RETRY_CONFIRMATION,
    SourceRetryRestoreError,
    build_source_retry_preview,
    execute_governed_source_retry,
    run_private_backup_restore_drill,
    summarize_nas_source_retry_restore_contract,
)
from business_cycle.storage.nas_live_postgres_dashboard import (
    DASHBOARD_READ_SQL,
    PsqlReadOnlyExecutor,
    build_nas_live_postgres_dashboard_snapshot,
    summarize_nas_live_postgres_dashboard_contract,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    CONFIRMATION,
    PsqlSubprocessExecutor,
    run_nas_postgres_live_revised_import,
    summarize_nas_postgres_live_revised_import_contract,
    load_nas_postgres_live_revised_import_contract,
)
from business_cycle.storage.postgres_macro_warehouse import (
    generate_postgres_schema_sql,
    load_postgres_macro_warehouse_contract,
    summarize_postgres_macro_warehouse_contract,
    table_contracts,
)
from business_cycle.storage.nas_transition_pit_backfill import (
    CONFIRMATION as PIT_CONFIRMATION,
    build_normalized_release_calendar_plan,
    run_transition_pit_backfill,
    summarize_nas_transition_pit_backfill_contract,
)
from business_cycle.storage.nas_broader_pit_release_replay import (
    CONFIRMATION as PHASE118_CONFIRMATION,
    build_release_calendar_schema_migration_sql,
    build_revision_aware_release_calendar_plan,
    run_nas_broader_pit_release_replay,
    summarize_nas_broader_pit_release_replay_contract,
)
from business_cycle.storage.nas_strict_replay_input_timeline import (
    run_nas_strict_replay_input_timeline,
    summarize_nas_strict_replay_input_timeline_contract,
)


def test_postgres_macro_warehouse_contract_passes() -> None:
    summary = summarize_postgres_macro_warehouse_contract()

    assert summary["result"] == "passed"
    assert summary["postgres_macro_warehouse_contract_ready"] is True
    assert summary["schema_table_count"] == 11
    assert summary["required_table_count"] == 11
    assert summary["missing_required_table_count"] == 0
    assert summary["table_without_primary_key_count"] == 0
    assert summary["pit_ready_schema"] is True
    assert summary["revised_vintage_separation_ready"] is True
    assert summary["vintage_required_column_missing_count"] == 0
    assert summary["release_calendar_revision_events_supported"] is True
    assert summary["release_calendar_required_column_missing_count"] == 0
    assert summary["source_artifact_hash_required"] is True
    assert summary["schema_requires_live_db"] is False
    assert summary["live_db_connection_attempt_count"] == 0
    assert summary["runtime_dependency_added_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["development_next_phase"] == 92


def test_postgres_macro_warehouse_tables_cover_required_families() -> None:
    contract = load_postgres_macro_warehouse_contract()
    tables = table_contracts(contract)

    assert set(tables) == set(contract["required_table_names"])
    assert contract["relationship_policy"]["migration_order"] == [
        "series_registry",
        "source_artifact",
        "observation_revised",
        "observation_vintage",
        "release_calendar",
        "indicator_value_snapshot",
        "evidence_snapshot",
        "dashboard_snapshot",
        "backtest_run",
        "backtest_result",
        "portfolio_policy_run",
    ]
    for table in tables.values():
        assert table["primary_key"]


def test_postgres_schema_sql_is_deterministic_and_pit_ready() -> None:
    sql = generate_postgres_schema_sql()

    assert "CREATE SCHEMA IF NOT EXISTS macro;" in sql
    assert "CREATE TABLE IF NOT EXISTS macro.observation_revised" in sql
    assert "CHECK (data_mode = 'revised')" in sql
    assert "CREATE TABLE IF NOT EXISTS macro.observation_vintage" in sql
    assert "realtime_start date NOT NULL" in sql
    assert "vintage_as_of date NOT NULL" in sql
    assert "release_timestamp_utc timestamptz NOT NULL" in sql
    assert "CHECK (data_mode = 'vintage_as_of')" in sql
    assert "CREATE TABLE IF NOT EXISTS macro.source_artifact" in sql
    assert "release_event_id text NOT NULL" in sql
    assert "PRIMARY KEY (series_key, release_event_id)" in sql
    assert "UNIQUE (content_hash)" in sql
    assert "CREATE TABLE IF NOT EXISTS macro.dashboard_snapshot" in sql
    assert "CHECK (research_only IS TRUE)" in sql
    assert "CREATE TABLE IF NOT EXISTS macro.portfolio_policy_run" in sql
    assert "CHECK (personalized_instruction_allowed IS FALSE)" in sql


def test_show_postgres_macro_warehouse_contract_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_postgres_macro_warehouse_contract.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "postgres_macro_warehouse_contract_ready=true" in result.stdout
    assert "schema_table_count=11" in result.stdout
    assert "pit_ready_schema=true" in result.stdout
    assert "schema_requires_live_db=false" in result.stdout
    assert "runtime_dependency_added_count=0" in result.stdout


class _FakeFullHistoryProvider:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        assert observation_start is None
        assert observation_end is None
        self.calls.append(series_id)
        return [
            SeriesObservation(series_id=series_id, date="2025-01-01", value="1.25"),
            SeriesObservation(series_id=series_id, date="2025-02-01", value="."),
        ]


class _FakeSqlExecutor:
    def __init__(self) -> None:
        self.statements: list[str] = []

    def execute(self, sql: str) -> str:
        self.statements.append(sql)
        return "ok"


def test_phase110_live_revised_import_contract_is_complete() -> None:
    summary = summarize_nas_postgres_live_revised_import_contract()

    assert summary["result"] == "passed"
    assert summary["nas_postgres_live_revised_import_contract_ready"] is True
    assert summary["postgres_schema_contract_ready"] is True
    assert summary["direct_series_count"] == 26
    assert summary["derived_role_count"] == 4
    assert summary["checkpoint_resume_ready"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_phase110_live_import_is_operator_gated_and_imports_each_series(
    tmp_path: Path,
) -> None:
    provider = _FakeFullHistoryProvider()
    executor = _FakeSqlExecutor()

    with pytest.raises(ValueError, match="operator confirmation"):
        run_nas_postgres_live_revised_import(
            execute_live=False,
            operator_confirmation=None,
            artifact_dir=tmp_path,
            provider=provider,
            executor=executor,
        )

    report = run_nas_postgres_live_revised_import(
        execute_live=True,
        operator_confirmation=CONFIRMATION,
        artifact_dir=tmp_path,
        provider=provider,
        executor=executor,
        retry_sleep=lambda _: None,
    )

    assert report["result"] == "passed"
    assert report["requested_series_count"] == 26
    assert report["completed_series_count"] == 26
    assert report["failed_series_count"] == 0
    assert report["observation_revised_row_count_planned"] == 52
    assert len(provider.calls) == 26
    assert len(executor.statements) == 27
    assert "CREATE SCHEMA IF NOT EXISTS macro" in executor.statements[0]
    assert all("ON CONFLICT" in sql for sql in executor.statements[1:])
    assert (tmp_path / "checkpoint.json").is_file()
    assert (tmp_path / "latest-import-report.json").is_file()
    assert len(list((tmp_path / "fred").glob("*.csv"))) == 26


def test_phase110_live_import_resumes_without_refetching(tmp_path: Path) -> None:
    first_provider = _FakeFullHistoryProvider()
    run_nas_postgres_live_revised_import(
        execute_live=True,
        operator_confirmation=CONFIRMATION,
        artifact_dir=tmp_path,
        provider=first_provider,
        executor=_FakeSqlExecutor(),
        retry_sleep=lambda _: None,
    )
    second_provider = _FakeFullHistoryProvider()
    second_executor = _FakeSqlExecutor()

    report = run_nas_postgres_live_revised_import(
        execute_live=True,
        operator_confirmation=CONFIRMATION,
        artifact_dir=tmp_path,
        provider=second_provider,
        executor=second_executor,
        retry_sleep=lambda _: None,
    )

    assert report["result"] == "passed"
    assert second_provider.calls == []
    assert len(second_executor.statements) == 1
    assert {row["status"] for row in report["results"]} == {"resumed_existing"}


def test_phase115_subset_retry_scope_is_validated_before_fetch(tmp_path: Path) -> None:
    provider = _FakeFullHistoryProvider()
    executor = _FakeSqlExecutor()
    report = run_nas_postgres_live_revised_import(
        execute_live=True,
        operator_confirmation=CONFIRMATION,
        artifact_dir=tmp_path / "subset",
        provider=provider,
        executor=executor,
        retry_sleep=lambda _: None,
        resume=False,
        series_ids=["BAA", "AAA"],
    )

    assert report["requested_series_count"] == 2
    assert provider.calls == ["AAA", "BAA"]
    with pytest.raises(ValueError, match="outside canonical source scope"):
        run_nas_postgres_live_revised_import(
            execute_live=True,
            operator_confirmation=CONFIRMATION,
            artifact_dir=tmp_path / "invalid",
            provider=provider,
            executor=executor,
            series_ids=["NOT_A_CANONICAL_SERIES"],
        )


def test_phase110_psql_executor_keeps_password_out_of_arguments() -> None:
    executor = PsqlSubprocessExecutor(
        "postgresql://business_cycle_app:private-value@macro_postgres:5432/business_cycle"
    )

    assert executor.environment["PGHOST"] == "macro_postgres"
    assert executor.environment["PGDATABASE"] == "business_cycle"
    assert executor.environment["PGPASSWORD"] == "private-value"
    assert "private-value" not in executor.executable


def test_show_phase110_live_revised_import_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_nas_postgres_live_revised_import.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_postgres_live_revised_import_contract_ready=true" in completed.stdout
    assert "direct_series_count=26" in completed.stdout
    assert "result=passed" in completed.stdout


def test_phase110_live_revised_import_closure_records_accepted_counts() -> None:
    summary = summarize_phase110_nas_postgres_live_revised_import_closure()

    assert summary["result"] == "passed"
    assert summary["phase110_closure_ready"] is True
    assert summary["schema_table_count"] == 11
    assert summary["completed_series_count"] == 26
    assert summary["failed_series_count"] == 0
    assert summary["observation_revised_row_count"] == 22131
    assert summary["observation_vintage_row_count"] == 0
    assert summary["checkpoint_resume_verified"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["development_next_phase"] == 111


def test_show_phase110_live_revised_import_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase110_nas_postgres_live_revised_import_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase110_closure_ready=true" in completed.stdout
    assert "observation_revised_row_count=22131" in completed.stdout
    assert "result=passed" in completed.stdout


def test_nas_compose_schedules_governed_refresh_and_keeps_https_private() -> None:
    compose = yaml.safe_load(Path("deploy/nas/compose.yaml").read_text(encoding="utf-8"))
    app = compose["services"]["business_cycle_app"]
    artifact_init = compose["services"]["macro_source_artifact_init"]
    worker = compose["services"]["macro_refresh_worker"]
    dockerfile = Path("Dockerfile.nas").read_text(encoding="utf-8")

    assert app["image"] == (
        "business-cycle-nas-app:phase119-login-and-strict-replay-timeline"
    )
    assert app["ports"] == [
        "127.0.0.1:18080:8000",
        "${BUSINESS_CYCLE_LAN_BIND_IP:-192.168.1.116}:18080:8000",
    ]
    assert app["environment"]["BUSINESS_CYCLE_APP_SECURE_COOKIE"] == "true"
    assert app["environment"]["BUSINESS_CYCLE_DASHBOARD_SHELL_TTL_SECONDS"] == "900"
    assert "BUSINESS_CYCLE_DECLARED_CYCLE_STATE_PATH" in app["environment"]
    assert "BUSINESS_CYCLE_SOURCE_OPERATIONS_STATUS_PATH" in app["environment"]
    assert "BUSINESS_CYCLE_RELEASE_AWARE_SCHEDULE_STATUS_PATH" in app["environment"]
    assert "BUSINESS_CYCLE_PIT_BACKFILL_STATUS_PATH" in app["environment"]
    assert "BUSINESS_CYCLE_BROADER_PIT_STATUS_PATH" in app["environment"]
    assert "BUSINESS_CYCLE_STRICT_REPLAY_TIMELINE_STATUS_PATH" in app["environment"]
    assert "BUSINESS_CYCLE_DATABASE_URL" in app["environment"]
    assert artifact_init["user"] == "0:0"
    assert artifact_init["restart"] == "no"
    assert artifact_init["network_mode"] == "none"
    assert "chown -R 1000:1000" in artifact_init["command"][0]
    assert "cycle_state_config:/var/lib/business-cycle/cycle-state" in (
        artifact_init["volumes"]
    )
    assert "cycle_state_config:/var/lib/business-cycle/cycle-state" in app["volumes"]
    assert worker["restart"] == "unless-stopped"
    assert "profiles" not in worker
    assert worker["volumes"] == [
        "macro_source_artifacts:/var/lib/business-cycle/source-artifacts"
    ]
    assert "business_cycle.service.nas_release_aware_refresh" in worker["command"]
    assert "--serve" in worker["command"]
    assert "--interval-seconds" not in worker["command"]
    assert "healthcheck" in worker
    assert worker["depends_on"]["macro_source_artifact_init"]["condition"] == (
        "service_completed_successfully"
    )
    assert "FRED_API_KEY" in worker["environment"]
    assert "BUSINESS_CYCLE_PIT_BACKFILL_OPERATOR_CONFIRMATION" in worker["environment"]
    assert "BUSINESS_CYCLE_PHASE118_OPERATOR_CONFIRMATION" in worker["environment"]
    assert "tailscale funnel" not in Path("deploy/nas/compose.yaml").read_text(
        encoding="utf-8"
    ).lower()
    assert "FROM python:3.10-slim-bookworm" in dockerfile
    assert "postgresql-client-16" in dockerfile
    assert "postgresql-client " not in dockerfile


def test_phase112_scheduled_refresh_is_atomic_bounded_and_redacted(
    tmp_path: Path,
) -> None:
    summary = summarize_nas_scheduled_revised_refresh_contract()
    calls: list[dict[str, object]] = []

    def successful_import(**kwargs: object) -> dict[str, object]:
        calls.append(kwargs)
        series_ids = load_nas_postgres_live_revised_import_contract()[
            "source_policy"
        ]["direct_series_ids"]
        return {
            "result": "passed",
            "requested_series_count": 26,
            "completed_series_count": 26,
            "failed_series_count": 0,
            "source_artifact_count": 26,
            "results": [
                {
                    "series_id": series_id,
                    "status": "imported",
                    "observation_count": 10,
                }
                for series_id in series_ids
            ],
        }

    status = run_scheduled_refresh_once(
        artifact_root=tmp_path,
        operator_confirmation=CONFIRMATION,
        import_runner=successful_import,
        now=lambda: datetime(2026, 7, 10, tzinfo=timezone.utc),
    )

    assert summary["result"] == "passed"
    assert summary["direct_series_count"] == 26
    assert status["refresh_state"] == "succeeded"
    assert status["completed_series_count"] == 26
    assert len(status["series_refresh_results"]) == 26
    assert status["candidate_phase_emitted"] is False
    assert status["current_phase_emitted"] is False
    assert json.loads((tmp_path / "refresh-status.json").read_text()) == status
    assert calls[0]["retry_count"] == 3
    assert calls[0]["resume"] is False

    schedule_root = tmp_path / "schedule"
    schedule_root.mkdir()
    (schedule_root / "refresh-status.json").write_text(
        json.dumps(status),
        encoding="utf-8",
    )
    sleeps: list[float] = []
    scheduled_runs: list[dict[str, object]] = []

    def scheduled_runner(**kwargs: object) -> dict[str, object]:
        scheduled_runs.append(kwargs)
        return status

    assert (
        serve_refresh_schedule(
            artifact_root=schedule_root,
            operator_confirmation=CONFIRMATION,
            interval_seconds=86400,
            initial_delay_seconds=86400,
            sleep=sleeps.append,
            max_runs=1,
            refresh_runner=scheduled_runner,
            now=lambda: datetime(2026, 7, 10, 12, tzinfo=timezone.utc),
        )
        == 0
    )
    assert sleeps == [43200.0]
    assert len(scheduled_runs) == 1

    def failed_import(**_: object) -> dict[str, object]:
        raise RuntimeError("private database details")

    failed = run_scheduled_refresh_once(
        artifact_root=tmp_path,
        operator_confirmation=CONFIRMATION,
        import_runner=failed_import,
        now=lambda: datetime(2026, 7, 11, tzinfo=timezone.utc),
    )
    assert failed["refresh_state"] == "failed"
    assert failed["error_class"] == "RuntimeError"
    assert failed["error_message_redacted"] == "refresh_execution_failed"
    assert "private database details" not in json.dumps(failed)

    with _exclusive_refresh_lock(tmp_path / "refresh.lock"):
        with pytest.raises(RuntimeError, match="already running"):
            run_scheduled_refresh_once(
                artifact_root=tmp_path,
                operator_confirmation=CONFIRMATION,
                import_runner=successful_import,
            )


class _FakeDashboardReadExecutor:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def query_json(self, sql: str) -> dict[str, object]:
        self.queries.append(sql)
        return _live_dashboard_fixture_payload()


def _live_dashboard_fixture_payload() -> dict[str, object]:
    direct_series = load_nas_postgres_live_revised_import_contract()[
        "source_policy"
    ]["direct_series_ids"]
    quarterly = {
        "BUSINV",
        "CBIC1",
        "DRBLACBS",
        "DRCLACBS",
        "FPIC1",
        "PRFIC1",
        "SLCEC1",
        "W006RC1Q027SBEA",
    }
    weekly = {"CCSA", "ICSA"}
    daily = {"AAA", "BAA", "FEDFUNDS"}
    series_rows = []
    artifact_rows = []
    observation_rows = []
    for index, series_id in enumerate(direct_series):
        frequency = (
            "quarterly"
            if series_id in quarterly
            else "weekly"
            if series_id in weekly
            else "daily"
            if series_id in daily
            else "monthly"
        )
        artifact_id = f"artifact::{series_id}"
        series_rows.append(
            {
                "series_key": series_id,
                "source_family": "FRED/ALFRED",
                "source_series_id": series_id,
                "source_title": f"Official {series_id}",
                "units": "Percent" if series_id in {"AAA", "BAA"} else "Index",
                "frequency": frequency,
                "seasonal_adjustment": "unknown",
                "geographic_scope": "United States",
                "source_url_without_secret": f"https://fred.stlouisfed.org/series/{series_id}",
                "source_identity_status": "verified",
                "updated_at_utc": "2026-07-10T00:00:00Z",
            },
        )
        artifact_rows.append(
            {
                "artifact_id": artifact_id,
                "source_family": "FRED/ALFRED",
                "source_url_without_secret": f"https://fred.stlouisfed.org/series/{series_id}",
                "source_series_or_release_id": series_id,
                "fetched_at_utc": "2026-07-10T00:00:00Z",
                "content_hash": f"hash-{series_id}",
                "adapter_id": "fred_revised_csv_phase110",
                "parser_version": "1.0",
                "validation_status": "validated",
            },
        )
        base = 4 if series_id == "AAA" else 6 if series_id == "BAA" else 100 + index
        for offset, observation_date in enumerate(
            ("2025-01-01", "2025-08-01", "2026-01-01", "2026-07-01"),
        ):
            observation_rows.append(
                {
                    "series_key": series_id,
                    "observation_date": observation_date,
                    "value_numeric": str(base + offset),
                    "value_text": None,
                    "unit": "Percent" if series_id in {"AAA", "BAA"} else "Index",
                    "data_mode": "revised",
                    "source_artifact_id": artifact_id,
                    "provenance_hash": f"provenance-{series_id}-{offset}",
                },
            )
    return {
        "transaction_read_only": "on",
        "database_latest_observation_date": "2026-07-04",
        "series_registry_rows": series_rows,
        "source_artifact_rows": artifact_rows,
        "observation_rows": observation_rows,
        "observation_revised_total_count": 22131,
        "observation_vintage_total_count": 0,
        "release_calendar_total_count": 0,
    }


def test_phase111_live_postgres_dashboard_contract_and_read_only_executor() -> None:
    summary = summarize_nas_live_postgres_dashboard_contract()
    executor = PsqlReadOnlyExecutor(
        "postgresql://business_cycle_app:private-value@macro_postgres:5432/business_cycle",
    )

    assert summary["result"] == "passed"
    assert summary["nas_live_postgres_dashboard_contract_ready"] is True
    assert summary["role_count"] == 39
    assert summary["derived_display_role_count"] == 4
    assert "default_transaction_read_only=on" in executor.environment["PGOPTIONS"]
    assert executor.environment["PGPASSWORD"] == "private-value"
    assert "private-value" not in executor.executable
    with pytest.raises(ValueError, match="SELECT/WITH"):
        executor.query_json("DELETE FROM macro.observation_revised")


def test_phase111_live_postgres_snapshot_materializes_values_charts_and_lineage() -> None:
    executor = _FakeDashboardReadExecutor()
    snapshot = build_nas_live_postgres_dashboard_snapshot(
        executor=executor,
        snapshot_as_of="2026-07-10",
    )
    roles = {row["role_id"]: row for row in snapshot["role_snapshots"]}
    spread = roles["recession_credit_financial_confirmation"]

    assert executor.queries == [DASHBOARD_READ_SQL]
    assert snapshot["role_snapshot_count"] == 39
    assert snapshot["role_with_revised_snapshot_count"] == 37
    assert snapshot["role_without_revised_snapshot_count"] == 2
    assert snapshot["chart_available_role_count"] == 37
    assert snapshot["series_snapshot_count"] == 26
    assert snapshot["source_artifact_snapshot_count"] == 26
    assert snapshot["observation_revised_total_count"] == 22131
    assert snapshot["observation_vintage_row_count"] == 0
    assert snapshot["trust_metadata"]["transaction_read_only"] is True
    assert spread["latest_revised_observations"][0]["value_numeric"] == "2"
    assert spread["source_lineage"][0]["component_series_ids"] == ["BAA", "AAA"]
    assert spread["chart_payload_detail"]["chart_available"] is True
    assert roles["boom_consumer_confidence"]["snapshot_status"] == "blocked"
    assert roles["growth_adp_employment"]["snapshot_status"] == "blocked"


def test_phase111_live_runtime_renders_private_chinese_chart_surface(
    tmp_path: Path,
) -> None:
    refresh_status_path = tmp_path / "refresh-status.json"
    refresh_status_path.write_text(
        json.dumps(
            {
                "refresh_state": "succeeded",
                "last_completed_at_utc": "2026-07-10T01:00:00Z",
                "next_scheduled_at_utc": "2026-07-11T01:00:00Z",
                "requested_series_count": 26,
                "completed_series_count": 26,
                "failed_series_count": 0,
            },
        ),
        encoding="utf-8",
    )
    runtime = build_nas_live_dashboard_runtime(
        executor=_FakeDashboardReadExecutor(),
        snapshot_as_of="2026-07-10",
        refresh_status_path=refresh_status_path,
    )
    bundle = runtime["dashboard_bundle"]
    html = next(
        page["html"] for page in bundle["html_pages"] if page["path"] == "/indicators"
    )
    status = bundle["api_payloads"]["service_status"]
    overview = next(
        page["html"] for page in bundle["html_pages"] if page["path"] == "/"
    )

    assert runtime["result"] == "passed"
    assert runtime["nas_live_postgres_dashboard_runtime_ready"] is True
    assert runtime["live_data_role_count"] == 37
    assert runtime["chart_available_role_count"] == 37
    assert status["dashboard_data_source"] == "live_postgres_read_only"
    assert status["live_db_connected"] is True
    assert status["refresh_status"]["refresh_state"] == "succeeded"
    assert status["source_refresh_health_status"] == "healthy"
    assert "官方資料更新狀態" in overview
    assert "最近更新成功" in overview
    assert "目前宣告景氣狀態" in overview
    assert "榮景" in overview
    assert "合法下一階段" in overview
    assert "檢視或確認榮景起始資訊" in overview
    assert html.count("<details>") == 37
    assert "查看今年／過去 1 年／過去 5 年走勢" in html
    assert 'class="interactive-chart"' in html
    assert "data-chart-points=" in html
    assert 'class="chart-tooltip"' in html
    assert "日期與數值" in html
    assert "pointermove" in html
    assert "ArrowLeft" in html
    assert "2026-07-01" in html
    assert "初領失業救濟金 U 型走勢" in html
    assert "目前數值使用 revised diagnostic snapshot" in html
    assert runtime["candidate_phase_emitted"] is False
    assert runtime["current_phase_emitted"] is False


def test_phase111_live_postgres_dashboard_closure_passes() -> None:
    summary = summarize_phase111_nas_live_postgres_dashboard_closure()

    assert summary["result"] == "passed"
    assert summary["live_deployment_accepted"] is True
    assert summary["app_container_healthy"] is True
    assert summary["live_db_connected"] is True
    assert summary["transaction_read_only_enforced"] is True
    assert summary["interactive_chart_tooltip_ready"] is True
    assert summary["role_count"] == 39
    assert summary["live_data_role_count"] == 37
    assert summary["source_blocked_role_count"] == 2
    assert summary["chart_available_role_count"] == 37
    assert summary["live_html_trend_details_count"] == 37
    assert summary["traditional_chinese_role_label_count"] == 39
    assert summary["observation_revised_row_count"] == 22131
    assert summary["observation_vintage_row_count"] == 0
    assert summary["production_behavior_change_count"] == 0


def test_show_phase111_live_postgres_dashboard_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase111_nas_live_postgres_dashboard_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase111_closure_ready=true" in completed.stdout
    assert "live_db_connected=true" in completed.stdout
    assert "role_count=39" in completed.stdout
    assert "phase111_closure_status=" in completed.stdout
    assert "result=passed" in completed.stdout


def test_phase114_release_calendar_and_failure_drilldown_are_source_specific() -> None:
    summary = summarize_nas_official_release_calendar_contract()
    series_ids = load_nas_postgres_live_revised_import_contract()[
        "source_policy"
    ]["direct_series_ids"]
    inputs = [
        {
            "series_id": series_id,
            "frequency": "monthly",
            "latest_observation_date": "2026-07-01",
            "freshness_status": "fresh",
        }
        for series_id in series_ids
    ]
    success_status = {
        "refresh_state": "succeeded",
        "last_run_state": "succeeded",
        "last_completed_at_utc": "2026-07-10T12:00:00Z",
        "series_refresh_results": [
            {
                "series_id": series_id,
                "status": "imported",
                "observation_count": 10,
                "error_class": None,
            }
            for series_id in series_ids
        ],
    }
    diagnostics = build_nas_official_release_diagnostics(
        as_of="2026-07-10",
        series_inputs=inputs,
        refresh_status=success_status,
    )

    assert summary["result"] == "passed"
    assert summary["release_family_count"] == 12
    assert summary["exact_schedule_family_count"] == 9
    assert diagnostics["release_calendar_runtime_ready"] is True
    assert diagnostics["series_diagnostic_count"] == 26
    assert diagnostics["official_source_delay_confirmed_count"] == 0
    assert diagnostics["observation_date_assumed_release_date_count"] == 0
    cadence = next(
        row
        for row in diagnostics["release_families"]
        if row["release_family_id"] == "moody_corporate_yields_via_fred"
    )
    assert cadence["release_monitor_status"] == "cadence_only_monitoring"
    assert cadence["official_source_delay_confirmed"] is False

    failed_status = {
        "refresh_state": "failed",
        "last_run_state": "failed",
        "last_completed_at_utc": "2026-07-10T12:00:00Z",
        "series_refresh_results": [
            {
                "series_id": "AAA",
                "status": "failed",
                "observation_count": 0,
                "error_class": "TimeoutError",
            }
        ],
    }
    failed = build_nas_official_release_diagnostics(
        as_of="2026-07-10",
        series_inputs=inputs,
        refresh_status=failed_status,
    )
    aaa = next(
        row for row in failed["series_refresh_diagnostics"] if row["series_id"] == "AAA"
    )
    baa = next(
        row for row in failed["series_refresh_diagnostics"] if row["series_id"] == "BAA"
    )
    assert aaa["failure_reason_codes"] == ["source_fetch_failed"]
    assert aaa["error_class"] == "TimeoutError"
    assert baa["failure_reason_codes"] == ["not_attempted_after_prior_failure"]
    assert failed["series_with_failure_reason_count"] == 26
    assert failed["refresh_failure_separated_from_source_delay"] is True


def test_phase114_source_operations_closure_and_script_pass() -> None:
    summary = summarize_phase114_nas_official_release_operations_closure()

    assert summary["result"] == "passed"
    assert summary["phase114_closure_ready"] is True
    assert summary["release_family_count"] == 12
    assert summary["series_diagnostic_count"] == 26
    assert summary["source_operations_page_authenticated_access"] is True
    assert summary["source_operations_api_authenticated_access"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase114_nas_official_release_operations_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "phase114_closure_ready=true" in completed.stdout
    assert "phase114_closure_status=" in completed.stdout
    assert "result=passed" in completed.stdout


def test_phase115_retry_preview_token_and_worker_subset_gate(tmp_path: Path) -> None:
    summary = summarize_nas_source_retry_restore_contract()
    series_ids = load_nas_postgres_live_revised_import_contract()[
        "source_policy"
    ]["direct_series_ids"]
    refresh_status = {
        "status_version": "phase114_refresh_status_v2",
        "run_id": "failed-run",
        "last_run_state": "failed",
        "last_completed_at_utc": "2026-07-10T00:00:00Z",
        "series_refresh_results": [
            {"series_id": "AAA", "status": "imported"},
            {"series_id": "BAA", "status": "failed", "error_class": "TimeoutError"},
        ],
    }
    refresh_root = tmp_path / "refresh"
    refresh_root.mkdir()
    (refresh_root / "refresh-status.json").write_text(
        json.dumps(refresh_status), encoding="utf-8"
    )
    preview = build_source_retry_preview(refresh_status)
    calls: list[dict[str, object]] = []

    def fake_refresh(**kwargs: object) -> dict[str, object]:
        calls.append(kwargs)
        return {"refresh_state": "succeeded"}

    assert summary["result"] == "passed"
    assert preview["retry_eligible"] is True
    assert preview["retry_candidate_count"] == len(series_ids) - 1
    assert preview["retry_series_ids"][0] == "BAA"
    with pytest.raises(SourceRetryRestoreError, match="stale or mismatched"):
        execute_governed_source_retry(
            preview_token="stale",
            confirmation=RETRY_CONFIRMATION,
            refresh_root=refresh_root,
            refresh_runner=fake_refresh,
        )
    result = execute_governed_source_retry(
        preview_token=preview["retry_preview_token"],
        confirmation=RETRY_CONFIRMATION,
        refresh_root=refresh_root,
        refresh_runner=fake_refresh,
    )
    assert result["retry_executed"] is True
    assert calls[0]["series_ids"] == preview["retry_series_ids"]
    assert result["candidate_phase_emitted"] is False
    assert result["current_phase_emitted"] is False


class _FakeBackupRestoreExecutor:
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run(self, command: list[str], *, environment: dict[str, str]) -> str:
        self.commands.append(command)
        assert environment["PGPASSWORD"] == "private-value"
        if command[:2] == ["pg_dump", "--version"]:
            return "pg_dump (PostgreSQL) 16.14"
        if command[0] == "pg_dump":
            output = next(
                value.split("=", 1)[1]
                for value in command
                if value.startswith("--file=")
            )
            Path(output).write_bytes(b"phase115-test-dump")
        if command[0] == "psql":
            if "SHOW server_version_num;" in command:
                return "160014"
            return json.dumps(
                {
                    "series_registry": 26,
                    "source_artifact": 26,
                    "observation_revised": 22131,
                    "observation_vintage": 0,
                    "release_calendar": 0,
                }
            )
        return ""


def test_phase115_backup_restore_drill_verifies_db_and_source_artifacts(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source-artifacts"
    source_root.mkdir()
    (source_root / "phase110").mkdir()
    (source_root / "phase110" / "AAA.csv").write_text("date,value\n", encoding="utf-8")
    executor = _FakeBackupRestoreExecutor()

    with pytest.raises(SourceRetryRestoreError, match="explicit backup restore"):
        run_private_backup_restore_drill(
            confirmation=None,
            operations_root=tmp_path / "phase115-rejected",
            source_artifact_root=source_root,
            executor=executor,
        )
    status = run_private_backup_restore_drill(
        confirmation=BACKUP_RESTORE_CONFIRMATION,
        database_url=(
            "postgresql://business_cycle_app:private-value@macro_postgres:5432/"
            "business_cycle"
        ),
        operations_root=source_root / "phase115",
        source_artifact_root=source_root,
        executor=executor,
        now=lambda: datetime(2026, 7, 10, tzinfo=timezone.utc),
    )

    assert status["backup_restore_state"] == "succeeded"
    assert status["row_count_match"] is True
    assert status["postgres_client_major"] == 16
    assert status["postgres_server_major"] == 16
    assert status["source_artifact_file_count"] == 1
    assert status["restored_source_artifact_file_count"] == 1
    assert status["staging_database_dropped"] is True
    assert status["secret_value_recorded"] is False
    assert [command[0] for command in executor.commands] == [
        "pg_dump",
        "psql",
        "psql",
        "pg_dump",
        "createdb",
        "pg_restore",
        "psql",
        "dropdb",
    ]
    persisted = json.loads(
        (source_root / "phase115" / "operations-status.json").read_text()
    )
    assert persisted == status
    assert json.loads(
        (
            source_root
            / "phase115"
            / "runs"
            / status["run_id"]
            / "drill-status.json"
        ).read_text()
    ) == status
    assert "private-value" not in json.dumps(status)


def test_phase116_fixed_daily_and_release_aware_schedule_are_deterministic(
    tmp_path: Path,
) -> None:
    summary = summarize_nas_release_aware_refresh_contract()
    daily = build_release_aware_schedule_preview(
        now=datetime(2026, 7, 11, 0, tzinfo=timezone.utc),
    )
    release = build_release_aware_schedule_preview(
        now=datetime(2026, 7, 14, 13, tzinfo=timezone.utc),
    )

    assert summary["result"] == "passed"
    assert daily["next_job"]["trigger_kind"] == "fixed_daily_full_refresh"
    assert daily["next_job"]["scheduled_at_local"].startswith(
        "2026-07-12T03:30:00+08:00"
    )
    assert daily["next_job"]["series_count"] == 26
    assert release["next_job"]["trigger_kind"] == "official_release_followup"
    assert release["next_job"]["release_family_id"] == (
        "bls_consumer_price_index"
    )
    assert release["next_job"]["series_ids"] == ["CPILFESL"]
    assert release["release_followup_availability_claim_count"] == 0
    assert release["cadence_or_reference_release_trigger_count"] == 0
    assert release["minimum_exact_calendar_horizon"] == "2026-08-06"
    with pytest.raises(ReleaseAwareRefreshError, match="timezone-aware"):
        build_release_aware_schedule_preview(now=datetime(2026, 7, 11))

    calls: list[dict[str, object]] = []

    def fake_refresh(**kwargs: object) -> dict[str, object]:
        calls.append(kwargs)
        return {"refresh_state": "succeeded"}

    now_values = iter(
        [
            datetime(2026, 7, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 7, 11, 19, 31, tzinfo=timezone.utc),
        ]
    )
    sleeps: list[float] = []
    assert (
        serve_release_aware_schedule(
            artifact_root=tmp_path / "phase116",
            refresh_root=tmp_path / "phase112",
            operator_confirmation=CONFIRMATION,
            sleep=sleeps.append,
            now=lambda: next(now_values),
            refresh_runner=fake_refresh,
            max_runs=1,
        )
        == 0
    )
    assert sleeps == [70200.0]
    assert len(calls) == 1
    assert len(calls[0]["series_ids"]) == 26
    status = load_release_aware_schedule_status(
        tmp_path / "phase116" / "schedule-status.json"
    )
    assert status["scheduler_state"] == "succeeded"
    assert status["last_trigger_kind"] == "fixed_daily_full_refresh"
    assert status["candidate_phase_emitted"] is False
    assert status["current_phase_emitted"] is False


def test_phase116_backup_retention_is_preview_only_and_preserves_unknown(
    tmp_path: Path,
) -> None:
    root = tmp_path / "phase115"
    runs = root / "runs"
    runs.mkdir(parents=True)
    for index in range(9):
        run = runs / f"202607{index + 1:02d}T000000000000Z"
        run.mkdir()
        (run / "drill-status.json").write_text(
            json.dumps({"backup_restore_state": "succeeded"}), encoding="utf-8"
        )
    for index in range(5):
        run = runs / f"202606{index + 1:02d}T000000000000Z"
        run.mkdir()
        (run / "drill-status.json").write_text(
            json.dumps({"backup_restore_state": "failed"}), encoding="utf-8"
        )
    (runs / "legacy_unknown_run").mkdir()

    preview = build_backup_retention_preview(root)

    assert preview["successful_run_count"] == 9
    assert preview["failed_run_count"] == 5
    assert preview["unknown_run_count"] == 1
    assert preview["retention_candidate_count"] == 4
    assert preview["automatic_deletion_enabled"] is False
    assert preview["delete_execution_count"] == 0
    assert (runs / "legacy_unknown_run").is_dir()


def test_phase116_release_aware_refresh_closure_and_script_pass() -> None:
    summary = summarize_phase116_nas_release_aware_refresh_closure()

    assert summary["result"] == "passed"
    assert summary["phase116_closure_ready"] is True
    assert summary["fixed_daily_time_zone"] == "Asia/Taipei"
    assert summary["fixed_daily_local_time"] == "03:30"
    assert summary["next_trigger_kind"] == "fixed_daily_full_refresh"
    assert summary["next_series_count"] == 26
    assert summary["release_aware_job_execution_count"] == 1
    assert summary["revised_direct_source_scope_complete"] is True
    assert summary["observation_revised_row_count"] == 22131
    assert summary["observation_vintage_row_count"] == 0
    assert summary["release_calendar_row_count"] == 0
    assert summary["macro_history_all_modes_complete"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase116_nas_release_aware_refresh_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "phase116_closure_ready=true" in completed.stdout
    assert "fixed_daily_local_time=03:30" in completed.stdout
    assert "macro_history_all_modes_complete=false" in completed.stdout
    assert "result=passed" in completed.stdout


class _FakeTransitionVintageProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None, str | None, int]] = []

    def fetch_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
        realtime_start: str | None = None,
        realtime_end: str | None = None,
        output_type: int = 1,
    ) -> list[AlfredObservation]:
        assert observation_start == "1998-01-01"
        assert observation_end is None
        assert realtime_start == "1998-01-01"
        assert realtime_end == "2026-07-10"
        assert output_type == 1
        self.calls.append((series_id, realtime_start, realtime_end, output_type))
        return [
            AlfredObservation(
                series_id=series_id,
                observation_date="2026-05-01",
                value="100.0",
                realtime_start="2026-06-01",
                realtime_end="2026-06-30",
            ),
            AlfredObservation(
                series_id=series_id,
                observation_date="2026-05-01",
                value="101.0",
                realtime_start="2026-07-01",
                realtime_end="9999-12-31",
            ),
        ]


def test_phase117_transition_pit_contract_calendar_and_live_import_are_safe(
    tmp_path: Path,
) -> None:
    summary = summarize_nas_transition_pit_backfill_contract()
    plan = build_normalized_release_calendar_plan()
    provider = _FakeTransitionVintageProvider()
    executor = _FakeSqlExecutor()

    assert summary["result"] == "passed"
    assert summary["transition_series_count"] == 13
    assert summary["transition_role_count"] == 14
    assert summary["alfred_output_type"] == 1
    assert plan["source_release_event_series_row_count"] == 85
    assert plan["normalized_release_calendar_row_count"] == 59
    assert plan["unresolved_weekly_reference_row_count"] == 12
    assert plan["deferred_revision_event_row_count"] == 14
    assert plan["observation_date_assumed_release_date_count"] == 0
    assert all(row["actual_release_at_utc"] is None for row in plan["normalized_release_calendar_rows"])

    with pytest.raises(ValueError, match="operator confirmation"):
        run_transition_pit_backfill(
            execute_live=False,
            operator_confirmation=None,
            artifact_dir=tmp_path / "rejected",
            provider=provider,
            executor=executor,
        )
    report = run_transition_pit_backfill(
        execute_live=True,
        operator_confirmation=PIT_CONFIRMATION,
        artifact_dir=tmp_path / "phase117",
        provider=provider,
        executor=executor,
        execution_date=date(2026, 7, 10),
    )

    assert report["result"] == "passed"
    assert report["completed_series_count"] == 13
    assert report["failed_series_count"] == 0
    assert report["observation_vintage_row_count_planned"] == 26
    assert report["normalized_release_calendar_row_count_planned"] == 59
    assert report["full_all_series_pit_history_complete"] is False
    assert report["candidate_phase_emitted"] is False
    assert report["current_phase_emitted"] is False
    assert len(provider.calls) == 13
    assert len(executor.statements) == 15
    pit_sql = "\n".join(executor.statements)
    assert "INSERT INTO macro.observation_vintage" in pit_sql
    assert "INSERT INTO macro.release_calendar" in pit_sql
    assert "23:59:59Z" in next(
        (tmp_path / "phase117" / "alfred").glob("*.csv")
    ).read_text(encoding="utf-8")
    assert not (Path("data/backtests") / "phase117").exists()
    closure = summarize_phase117_transition_pit_backfill_closure()
    assert closure["result"] == "passed"
    assert closure["phase117_closure_ready"] is True
    assert closure["completed_series_count"] == 13
    assert closure["failed_series_count"] == 0
    assert closure["observation_revised_row_count"] == 22131
    assert closure["observation_vintage_row_count"] == 42957
    assert closure["release_calendar_row_count"] == 59
    assert closure["lan_and_tailscale_loopback_bindings_ready"] is True
    assert closure["full_all_series_pit_history_complete"] is False
    assert closure["candidate_phase_emitted"] is False
    assert closure["current_phase_emitted"] is False
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase117_transition_pit_backfill_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "phase117_closure_ready=true" in completed.stdout
    assert "observation_vintage_row_count=42957" in completed.stdout
    assert "full_all_series_pit_history_complete=false" in completed.stdout
    assert "result=passed" in completed.stdout


class _FakeStrictReplayAuditExecutor:
    def query_json(self, sql: str) -> dict[str, object]:
        assert "macro.observation_vintage" in sql
        assert "realtime_start <= s.as_of" in sql
        assert "realtime_end >= s.as_of" in sql
        series_ids = load_nas_postgres_live_revised_import_contract()[
            "source_policy"
        ]["direct_series_ids"]
        scenario_rows = []
        for scenario_id, as_of in (
            ("dotcom_cycle_2000_2003", "2000-01-31"),
            ("global_financial_crisis_2007_2009", "2007-01-31"),
            ("covid_recession_2020", "2020-01-31"),
            ("euro_debt_slowdown_2011_2012", "2011-01-31"),
            ("late_cycle_2018_2019", "2018-01-31"),
        ):
            scenario_rows.append(
                {
                    "scenario_id": scenario_id,
                    "as_of": as_of,
                    "available_series_ids": series_ids,
                }
            )
        return {
            "transaction_read_only": "on",
            "database_vintage_series_count": len(series_ids),
            "scenario_rows": scenario_rows,
        }


class _FakeMonthlyReplayTimelineExecutor:
    def query_json(self, sql: str) -> dict[str, object]:
        assert "generate_series" in sql
        assert "macro.observation_vintage" in sql
        series_ids = load_nas_postgres_live_revised_import_contract()[
            "source_policy"
        ]["direct_series_ids"]
        scenario_windows = (
            ("dotcom_cycle_2000_2003", 2000, 1, 2003, 12),
            ("global_financial_crisis_2007_2009", 2007, 1, 2009, 12),
            ("covid_recession_2020", 2020, 1, 2021, 12),
            ("euro_debt_slowdown_2011_2012", 2011, 1, 2012, 12),
            ("late_cycle_2018_2019", 2018, 1, 2019, 12),
        )
        rows = []
        for scenario_id, start_year, start_month, end_year, end_month in scenario_windows:
            year, month = start_year, start_month
            while (year, month) <= (end_year, end_month):
                available = list(series_ids)
                if scenario_id == "dotcom_cycle_2000_2003" and (year, month) == (
                    2000,
                    1,
                ):
                    available = available[1:]
                rows.append(
                    {
                        "scenario_id": scenario_id,
                        "as_of": f"{year:04d}-{month:02d}-28",
                        "available_series_ids": available,
                    }
                )
                month += 1
                if month == 13:
                    year += 1
                    month = 1
        assert len(rows) == 156
        return {"transaction_read_only": "on", "timeline_rows": rows}


class _FakeBroaderVintageProvider(_FakeTransitionVintageProvider):
    def fetch_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
        realtime_start: str | None = None,
        realtime_end: str | None = None,
        output_type: int = 1,
    ) -> list[AlfredObservation]:
        assert realtime_end == "9999-12-31"
        return super().fetch_observations(
            series_id,
            observation_start=observation_start,
            observation_end=observation_end,
            realtime_start=realtime_start,
            realtime_end="2026-07-10",
            output_type=output_type,
        )


def test_phase118_broader_pit_revision_calendar_and_input_audit_are_safe(
    tmp_path: Path,
) -> None:
    summary = summarize_nas_broader_pit_release_replay_contract()
    plan = build_revision_aware_release_calendar_plan()
    migration = build_release_calendar_schema_migration_sql()
    provider = _FakeBroaderVintageProvider()
    executor = _FakeSqlExecutor()

    assert summary["result"] == "passed"
    assert summary["broader_pit_series_count"] == 13
    assert summary["expected_all_direct_series_count_after"] == 26
    assert plan["normalized_release_event_row_count"] == 85
    assert plan["weekly_reference_event_row_count"] == 12
    assert plan["revision_event_row_count"] == 21
    assert plan["deferred_release_event_row_count"] == 0
    assert plan["duplicate_release_event_id_count"] == 0
    assert all(row["actual_release_at_utc"] is None for row in plan["normalized_release_event_rows"])
    for row in plan["normalized_release_event_rows"]:
        if row["series_key"] not in {"ICSA", "CCSA"}:
            continue
        release_day = date.fromisoformat(row["expected_release_at_utc"][:10])
        reference_end = date.fromisoformat(row["reference_period_end"])
        expected_lag = 5 if row["series_key"] == "ICSA" else 12
        assert (release_day - reference_end).days == expected_lag
        assert row["reference_period_precision"] == "official_week_ending_rule"
    assert "Phase118 calendar guard rejected unexpected live rows" in migration
    assert "PRIMARY KEY (series_key, release_event_id)" in migration

    with pytest.raises(ValueError, match="explicit confirmation"):
        run_nas_broader_pit_release_replay(
            execute_live=False,
            operator_confirmation=None,
            artifact_dir=tmp_path / "rejected",
            provider=provider,
            executor=executor,
            audit_executor=_FakeStrictReplayAuditExecutor(),
        )
    report = run_nas_broader_pit_release_replay(
        execute_live=True,
        operator_confirmation=PHASE118_CONFIRMATION,
        artifact_dir=tmp_path / "phase118",
        provider=provider,
        executor=executor,
        audit_executor=_FakeStrictReplayAuditExecutor(),
        execution_date=date(2026, 7, 10),
    )

    assert report["result"] == "passed"
    assert report["completed_series_count"] == 13
    assert report["failed_series_count"] == 0
    assert report["broader_observation_vintage_row_count_planned"] == 26
    assert report["normalized_release_event_row_count_planned"] == 85
    assert report["strict_replay_input_audit"][
        "scenario_with_all_required_series_count"
    ] == 5
    assert report["model_execution_count"] == 0
    assert report["backtest_execution_count"] == 0
    assert report["candidate_phase_emitted"] is False
    assert report["current_phase_emitted"] is False
    assert len(provider.calls) == 13
    assert len(executor.statements) == 15
    sql = "\n".join(executor.statements)
    assert "INSERT INTO macro.release_calendar" in sql
    assert "INSERT INTO macro.observation_vintage" in sql
    assert not (Path("data/backtests") / "phase118").exists()
    completed = subprocess.run(
        [sys.executable, "scripts/show_nas_broader_pit_release_replay.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "normalized_release_event_row_count=85" in completed.stdout
    assert "revision_event_row_count=21" in completed.stdout
    assert "result=passed" in completed.stdout

    closure = summarize_phase118_broader_pit_release_replay_closure()
    assert closure["result"] == "passed"
    assert closure["phase118_closure_ready"] is True
    assert closure["all_direct_pit_series_count"] == 26
    assert closure["observation_vintage_row_count"] == 76848
    assert closure["release_calendar_row_count"] == 85
    assert closure["strict_replay_scenario_with_all_inputs_count"] == 2
    assert closure["strict_replay_scenario_with_partial_inputs_count"] == 3
    assert closure["macro_history_all_modes_complete"] is False
    assert closure["candidate_phase_emitted"] is False
    assert closure["current_phase_emitted"] is False
    closure_cli = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase118_broader_pit_release_replay_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "phase118_closure_ready=true" in closure_cli.stdout
    assert "all_direct_pit_series_count=26" in closure_cli.stdout
    assert "result=passed" in closure_cli.stdout


def test_phase119_monthly_strict_replay_inputs_abstain_without_model_execution(
    tmp_path: Path,
) -> None:
    summary = summarize_nas_strict_replay_input_timeline_contract()
    executor = _FakeMonthlyReplayTimelineExecutor()

    assert summary["result"] == "passed"
    assert summary["scenario_count"] == 5
    assert summary["expected_month_end_row_count"] == 156
    assert summary["required_direct_series_count"] == 26
    assert summary["private_lan_http_login_contract_ready"] is True
    assert summary["professional_dashboard_ux_blueprint_ready"] is True
    with pytest.raises(ValueError, match="--execute-live"):
        run_nas_strict_replay_input_timeline(
            execute_live=False,
            output=tmp_path / "rejected.json",
            executor=executor,
        )
    artifact = run_nas_strict_replay_input_timeline(
        execute_live=True,
        output=tmp_path / "phase119-timeline.json",
        executor=executor,
    )

    assert artifact["result"] == "passed"
    assert artifact["month_end_row_count"] == 156
    assert artifact["complete_month_count"] == 155
    assert artifact["abstention_month_count"] == 1
    abstained = [
        row for row in artifact["timeline_rows"] if row["abstention_required"]
    ]
    assert len(abstained) == 1
    assert abstained[0]["missing_series_count"] == 1
    assert artifact["revised_fallback_count"] == 0
    assert artifact["lookback_sufficiency_claim_count"] == 0
    assert artifact["model_execution_count"] == 0
    assert artifact["historical_accuracy_metric_count"] == 0
    assert artifact["economic_performance_metric_count"] == 0
    assert artifact["backtest_execution_count"] == 0
    assert artifact["candidate_phase_emitted"] is False
    assert artifact["current_phase_emitted"] is False
    assert (tmp_path / "phase119-timeline.json").exists()
    assert not (Path("data/backtests") / "phase119").exists()
    completed = subprocess.run(
        [sys.executable, "scripts/show_nas_strict_replay_input_timeline.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "expected_month_end_row_count=156" in completed.stdout
    assert "professional_dashboard_ux_blueprint_ready=true" in completed.stdout
    assert "result=passed" in completed.stdout

    closure = summarize_phase119_private_login_strict_replay_ux_closure()
    assert closure["result"] == "passed"
    assert closure["phase119_closure_ready"] is True
    assert closure["private_lan_http_login_fixed"] is True
    assert closure["tailscale_https_secure_cookie_preserved"] is True
    assert closure["timeline_month_end_row_count"] == 156
    assert closure["complete_month_count"] == 48
    assert closure["abstention_month_count"] == 108
    assert closure["professional_dashboard_ux_assessment_ready"] is True
    assert closure["candidate_phase_emitted"] is False
    assert closure["current_phase_emitted"] is False
    closure_cli = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase119_private_login_strict_replay_ux_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "phase119_closure_ready=true" in closure_cli.stdout
    assert "complete_month_count=48" in closure_cli.stdout
    assert "abstention_month_count=108" in closure_cli.stdout
    assert "result=passed" in closure_cli.stdout


def test_phase115_source_retry_restore_closure_and_script_pass() -> None:
    summary = summarize_phase115_nas_source_retry_restore_closure()

    assert summary["result"] == "passed"
    assert summary["phase115_closure_ready"] is True
    assert summary["live_retry_candidate_count"] == 0
    assert summary["live_retry_execution_count"] == 0
    assert summary["backup_restore_state"] == "succeeded"
    assert summary["database_row_count_match"] is True
    assert summary["source_artifact_restore_count_match"] is True
    assert summary["staging_database_dropped"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase115_nas_source_retry_restore_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "phase115_closure_ready=true" in completed.stdout
    assert "backup_restore_state=succeeded" in completed.stdout
    assert "result=passed" in completed.stdout


def test_phase112_scheduled_refresh_closure_and_script_pass() -> None:
    summary = summarize_phase112_nas_scheduled_revised_refresh_closure()

    assert summary["result"] == "passed"
    assert summary["phase112_closure_ready"] is True
    assert summary["refresh_state"] == "scheduled"
    assert summary["last_run_state"] == "succeeded"
    assert summary["completed_series_count"] == 26
    assert summary["source_refresh_health_status"] == "healthy"
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase112_nas_scheduled_revised_refresh_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "phase112_closure_ready=true" in completed.stdout
    assert "phase112_closure_status=" in completed.stdout
    assert "result=passed" in completed.stdout
