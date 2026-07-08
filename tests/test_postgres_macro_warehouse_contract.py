from __future__ import annotations

import subprocess
import sys

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
