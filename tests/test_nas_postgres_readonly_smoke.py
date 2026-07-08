from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.storage.nas_postgres_readonly_smoke import (
    build_nas_postgres_readonly_smoke,
    summarize_nas_postgres_readonly_smoke,
)

pytestmark = pytest.mark.archive_regression


def test_nas_postgres_readonly_smoke_summary_passes() -> None:
    summary = summarize_nas_postgres_readonly_smoke()

    assert summary["result"] == "passed"
    assert summary["nas_postgres_readonly_smoke_contract_ready"] is True
    assert summary["nas_postgres_readonly_smoke_ready"] is True
    assert summary["postgres_macro_warehouse_dependency_ready"] is True
    assert summary["phase92_revised_import_dependency_ready"] is True
    assert summary["phase98_lifecycle_dependency_ready"] is True
    assert summary["fixture_driver_ready"] is True
    assert summary["readonly_query_contract_count"] == 4
    assert summary["readonly_query_pass_count"] == 4
    assert summary["readonly_result_set_count"] == 4
    assert summary["readonly_result_row_count"] == 16
    assert summary["readonly_required_column_missing_count"] == 0
    assert summary["forbidden_sql_rejected_count"] == 12
    assert summary["forbidden_sql_accepted_count"] == 0


def test_nas_postgres_readonly_smoke_query_results_are_fixture_backed() -> None:
    smoke = build_nas_postgres_readonly_smoke()

    results = smoke["query_results"]
    assert [result["query_passed"] for result in results] == [True] * 4
    assert [result["row_count"] for result in results] == [5, 5, 5, 1]
    assert all(result["fixture_backed"] is True for result in results)
    assert all(result["live_db_connection_attempted"] is False for result in results)
    assert all(result["postgres_write_attempted"] is False for result in results)


def test_nas_postgres_readonly_smoke_preserves_no_live_boundaries() -> None:
    smoke = build_nas_postgres_readonly_smoke()

    assert smoke["live_db_connection_attempt_count"] == 0
    assert smoke["postgres_read_attempt_count"] == 0
    assert smoke["postgres_write_attempt_count"] == 0
    assert smoke["schema_migration_attempt_count"] == 0
    assert smoke["runtime_dependency_added_count"] == 0
    assert smoke["network_bind_attempt_count"] == 0
    assert smoke["live_server_start_attempt_count"] == 0
    assert smoke["live_fetch_attempt_count"] == 0
    assert smoke["repo_output_written_count"] == 0
    assert smoke["public_output_count"] == 0
    assert smoke["frontend_database_access_allowed"] is False
    assert smoke["frontend_api_key_allowed"] is False
    assert smoke["candidate_phase_emitted"] is False
    assert smoke["current_phase_emitted"] is False


def test_show_nas_postgres_readonly_smoke_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_postgres_readonly_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_postgres_readonly_smoke_ready=true" in result.stdout
    assert "readonly_query_pass_count=4" in result.stdout
    assert "forbidden_sql_rejected_count=12" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_postgres_readonly_smoke_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_nas_postgres_readonly_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_postgres_readonly_smoke_ready=true" in result.stdout
    assert "readonly_query_pass_count=4" in result.stdout
    assert "postgres_write_attempt_count=0" in result.stdout
    assert "public_output_count=0" in result.stdout
