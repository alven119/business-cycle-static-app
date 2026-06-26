from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase39_current_research_snapshot_closure import (
    summarize_phase39_current_research_snapshot_closure,
)


def test_phase39_current_research_snapshot_closure_passes() -> None:
    summary = summarize_phase39_current_research_snapshot_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["phase37_closure_result"] == "passed"
    assert summary["current_dashboard_view_ready"] is True
    assert summary["dashboard_view_count"] == 8
    assert summary["alpha36_freeze_hash_valid"] is True
    assert summary["alpha35_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["economic_performance_metric_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["development_next_phase"] == 40
    assert summary["phase39_closure_status"] == (
        "closed_ci_regressions_fixed_current_research_snapshot_dashboard_available_"
        "no_current_phase_or_performance"
    )


def test_show_phase39_current_research_snapshot_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase39_current_research_snapshot_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "phase39_closure_status=" in result.stdout
