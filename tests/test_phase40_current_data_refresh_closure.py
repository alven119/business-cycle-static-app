from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase40_current_data_refresh_closure import (
    summarize_phase40_current_data_refresh_closure,
)


def test_phase40_current_data_refresh_closure_passes() -> None:
    summary = summarize_phase40_current_data_refresh_closure()

    assert summary["result"] == "passed"
    assert summary["current_data_refresh_contract_ready"] is True
    assert summary["current_data_refresh_runtime_ready"] is True
    assert summary["current_dashboard_refresh_panel_ready"] is True
    assert summary["ci_hermetic_refresh_tests_ready"] is True
    assert summary["alpha37_freeze_hash_valid"] is True
    assert summary["alpha36_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["economic_performance_metric_count"] == 0
    assert summary["development_next_phase"] == 41
    assert (
        summary["phase40_closure_status"]
        == "closed_controlled_current_data_refresh_available_no_current_phase_or_performance"
    )


def test_show_phase40_current_data_refresh_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase40_current_data_refresh_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "current_data_refresh_runtime_ready=true" in result.stdout
    assert "phase40_closure_status=closed_controlled_current_data_refresh" in result.stdout
    assert "result=passed" in result.stdout
