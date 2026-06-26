from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase40_current_data_refresh import (
    summarize_phase40_current_data_refresh,
)


def test_phase40_current_data_refresh_audit_passes() -> None:
    summary = summarize_phase40_current_data_refresh()

    assert summary["result"] == "passed"
    assert summary["current_data_refresh_contract_ready"] is True
    assert summary["current_data_refresh_runtime_ready"] is True
    assert summary["current_snapshot_refresh_integration_ready"] is True
    assert summary["current_dashboard_refresh_panel_ready"] is True
    assert summary["ci_hermetic_refresh_tests_ready"] is True
    assert summary["live_fetch_attempted"] is False
    assert summary["live_fetch_skipped_reason"] == "live_fetch_disabled_by_cli"
    assert summary["fixture_fallback_explicit"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["forbidden_repo_output_count"] == 0


def test_show_phase40_current_data_refresh_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase40_current_data_refresh.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "current_data_refresh_runtime_ready=true" in result.stdout
    assert "current_dashboard_refresh_panel_ready=true" in result.stdout
    assert "result=passed" in result.stdout
