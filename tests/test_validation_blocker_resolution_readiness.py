from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.validation_blocker_resolution_readiness import (
    summarize_validation_blocker_resolution_readiness,
)


def test_validation_blocker_resolution_readiness_passes() -> None:
    summary = summarize_validation_blocker_resolution_readiness()

    assert summary["validation_blocker_resolution_readiness_ready"] is True
    assert summary["genuine_blocker_resolution_protocol_ready"] is True
    assert summary["genuine_blocker_work_package_registry_ready"] is True
    assert summary["reviewed_genuine_blocker_count"] == 5
    assert summary["work_package_count"] == 5
    assert summary["blocker_without_work_package_count"] == 0
    assert summary["work_package_without_source_blocker_count"] == 0
    assert summary["work_package_without_allowed_action_count"] == 0
    assert summary["work_package_without_prohibited_action_count"] == 0
    assert summary["work_package_without_completion_gate_count"] == 0
    assert summary["false_resolution_count"] == 0
    assert summary["blocker_resolution_executed"] is False
    assert summary["scenario_promoted_to_comparable_count"] == 0
    assert summary["evidence_rule_modified_count"] == 0
    assert summary["predicted_mapping_rule_modified_count"] == 0
    assert summary["formal_decision_contract_modified_count"] == 0
    assert summary["threshold_modified_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["new_accuracy_metric_computed_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["backtest_execution_enabled"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_show_validation_blocker_resolution_readiness_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_validation_blocker_resolution_readiness.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase=32" in result.stdout
    assert "validation_blocker_resolution_readiness_ready=true" in result.stdout
    assert "reviewed_genuine_blocker_count=5" in result.stdout
    assert "historical_accuracy_metric_count=5" in result.stdout
