from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from business_cycle.audits.phase110_nas_postgres_live_revised_import_closure import (
    summarize_phase110_nas_postgres_live_revised_import_closure,
)
from business_cycle.data_sources import SeriesObservation
from business_cycle.storage.nas_postgres_live_revised_import import (
    CONFIRMATION,
    PsqlSubprocessExecutor,
    run_nas_postgres_live_revised_import,
    summarize_nas_postgres_live_revised_import_contract,
)
from business_cycle.storage.postgres_macro_warehouse import (
    generate_postgres_schema_sql,
    load_postgres_macro_warehouse_contract,
    summarize_postgres_macro_warehouse_contract,
    table_contracts,
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


def test_phase110_nas_compose_keeps_worker_manual_and_https_private() -> None:
    compose = yaml.safe_load(Path("deploy/nas/compose.yaml").read_text(encoding="utf-8"))
    app = compose["services"]["business_cycle_app"]
    worker = compose["services"]["macro_refresh_worker"]

    assert app["image"] == "business-cycle-nas-app:phase110-revised-import"
    assert app["ports"] == ["127.0.0.1:18080:8000"]
    assert app["environment"]["BUSINESS_CYCLE_APP_SECURE_COOKIE"] == "true"
    assert worker["profiles"] == ["manual-revised-import"]
    assert worker["restart"] == "no"
    assert worker["volumes"] == [
        "macro_source_artifacts:/var/lib/business-cycle/source-artifacts"
    ]
    assert "business_cycle.service.nas_revised_import_worker" in worker["command"]
    assert "FRED_API_KEY" in worker["environment"]
    assert "tailscale funnel" not in Path("deploy/nas/compose.yaml").read_text(
        encoding="utf-8"
    ).lower()
