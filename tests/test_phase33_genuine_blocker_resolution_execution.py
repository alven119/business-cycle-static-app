from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase33_genuine_blocker_resolution_execution import (
    summarize_phase33_genuine_blocker_resolution_execution,
)


def test_phase33_genuine_blocker_resolution_execution_passes() -> None:
    summary = summarize_phase33_genuine_blocker_resolution_execution()

    assert summary["result"] == "passed"
    assert summary["genuine_blocker_resolution_execution_ready"] is True
    assert summary["post_resolution_validation_rerun_ready"] is True
    assert summary["work_package_count"] == 5
    assert summary["safe_executable_work_package_count"] == 5
    assert summary["executed_work_package_count"] == 5
    assert summary["still_genuine_blocked_work_package_count"] == 5
    assert summary["work_package_without_execution_reason_count"] == 0
    assert summary["pre_resolution_blocked_scenario_count"] == 5
    assert summary["post_resolution_blocked_scenario_count"] == 5
    assert summary["pre_resolution_comparable_scenario_count"] == 0
    assert summary["post_resolution_comparable_scenario_count"] == 0
    assert summary["false_resolution_count"] == 0
    assert summary["scenario_promoted_without_required_evidence_count"] == 0
    assert summary["scenario_promoted_by_taxonomy_only_count"] == 0
    assert summary["scenario_promoted_by_modern_proxy_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["new_accuracy_metric_computed_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_show_phase33_genuine_blocker_resolution_execution_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase33_genuine_blocker_resolution_execution.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "phase33_resolution_progress_status=" in result.stdout
