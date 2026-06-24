from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase33_blocker_resolution_execution_closure import (
    summarize_phase33_blocker_resolution_execution_closure,
)


def test_phase33_blocker_resolution_execution_closure_passes() -> None:
    summary = summarize_phase33_blocker_resolution_execution_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["genuine_blocker_resolution_execution_ready"] is True
    assert summary["post_resolution_validation_rerun_ready"] is True
    assert summary["work_package_count"] == 5
    assert summary["safe_executable_work_package_count"] == 5
    assert summary["executed_work_package_count"] == 5
    assert summary["still_genuine_blocked_work_package_count"] == 5
    assert summary["pre_resolution_blocked_scenario_count"] == 5
    assert summary["post_resolution_blocked_scenario_count"] == 5
    assert summary["false_resolution_count"] == 0
    assert summary["evidence_rule_modified_count"] == 0
    assert summary["predicted_mapping_rule_modified_count"] == 0
    assert summary["threshold_modified_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["alpha29_freeze_hash_valid"] is True
    assert summary["alpha28_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["economic_validation_status"] == (
        "blocker_resolution_execution_research_only_no_performance"
    )
    assert summary["development_next_phase"] == 34
    assert summary["phase33_closure_status"] == (
        "closed_genuine_blocker_resolution_execution_research_only_no_performance"
    )


def test_show_phase33_blocker_resolution_execution_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase33_blocker_resolution_execution_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "development_next_phase=34" in result.stdout
