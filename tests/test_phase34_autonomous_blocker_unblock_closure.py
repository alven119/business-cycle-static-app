from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase34_autonomous_blocker_unblock_closure import (
    summarize_phase34_autonomous_blocker_unblock_closure,
)


def test_phase34_autonomous_blocker_unblock_closure_passes() -> None:
    summary = summarize_phase34_autonomous_blocker_unblock_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["autonomous_blocker_unblock_runtime_ready"] is True
    assert summary["post_unblock_validation_rerun_ready"] is True
    assert summary["pre_resolution_blocked_scenario_count"] == 5
    assert summary["post_resolution_blocked_scenario_count"] == 0
    assert summary["post_resolution_comparable_scenario_count"] == 0
    assert summary["false_resolution_count"] == 0
    assert summary["alpha30_freeze_hash_valid"] is True
    assert summary["alpha29_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["economic_validation_status"] == (
        "autonomous_blocker_unblock_attempted_research_only_no_performance"
    )
    assert summary["development_next_phase"] == 35
    assert summary["phase34_resolution_progress_status"] == (
        "blocked_scenario_count_reduced"
    )
    assert summary["phase34_closure_status"] == (
        "closed_autonomous_blocker_unblock_research_only_no_performance"
    )


def test_show_phase34_autonomous_blocker_unblock_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase34_autonomous_blocker_unblock_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase34_closure_status=" in result.stdout
    assert "post_resolution_blocked_scenario_count=0" in result.stdout
    assert "result=passed" in result.stdout
