from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase91_postgres_macro_warehouse_closure import (
    summarize_phase91_postgres_macro_warehouse_closure,
)


def test_phase91_postgres_macro_warehouse_closure_passes() -> None:
    summary = summarize_phase91_postgres_macro_warehouse_closure()

    assert summary["result"] == "passed"
    assert summary["phase91_closure_ready"] is True
    assert summary["postgres_macro_warehouse_contract_ready"] is True
    assert summary["nas_dynamic_service_dependency_ready"] is True
    assert summary["schema_table_count"] == 11
    assert summary["missing_required_table_count"] == 0
    assert summary["pit_ready_schema"] is True
    assert summary["revised_vintage_separation_ready"] is True
    assert summary["vintage_required_column_missing_count"] == 0
    assert summary["revised_first_backfill_policy_present"] is True
    assert summary["vintage_backfill_plan_present"] is True
    assert summary["schema_sql_generated"] is True
    assert summary["schema_requires_live_db"] is False
    assert summary["live_db_connection_attempt_count"] == 0
    assert summary["runtime_dependency_added_count"] == 0
    assert summary["frontend_database_access_allowed"] is False
    assert summary["frontend_api_key_allowed"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["development_next_phase"] == 92


def test_show_phase91_postgres_macro_warehouse_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase91_postgres_macro_warehouse_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase91_closure_ready=true" in result.stdout
    assert "postgres_macro_warehouse_contract_ready=true" in result.stdout
    assert "nas_dynamic_service_dependency_ready=true" in result.stdout
    assert "development_next_phase=92" in result.stdout
    assert "result=passed" in result.stdout
