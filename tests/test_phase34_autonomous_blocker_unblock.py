from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase34_autonomous_blocker_unblock import (
    summarize_phase34_autonomous_blocker_unblock,
)


def test_phase34_autonomous_blocker_unblock_audit_passes() -> None:
    summary = summarize_phase34_autonomous_blocker_unblock()

    assert summary["result"] == "passed"
    assert summary["autonomous_blocker_unblock_runtime_ready"] is True
    assert summary["post_unblock_validation_rerun_ready"] is True
    assert summary["attempted_fix_iteration_count"] == 2
    assert summary["pre_resolution_blocked_scenario_count"] == 5
    assert summary["post_resolution_blocked_scenario_count"] == 0
    assert summary["post_resolution_comparable_scenario_count"] == 0
    assert summary["safe_fixable_blocker_count"] == 0
    assert summary["unresolved_safe_fixable_blocker_count"] == 0
    assert summary["false_resolution_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0


def test_show_phase34_autonomous_blocker_unblock_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase34_autonomous_blocker_unblock.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "autonomous_blocker_unblock_runtime_ready=true" in result.stdout
    assert "post_resolution_blocked_scenario_count=0" in result.stdout
    assert "result=passed" in result.stdout
