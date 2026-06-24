from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase32_genuine_blocker_resolution_plan_closure import (
    summarize_phase32_genuine_blocker_resolution_plan_closure,
)


def test_phase32_genuine_blocker_resolution_plan_closure_passes() -> None:
    summary = summarize_phase32_genuine_blocker_resolution_plan_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["genuine_blocker_resolution_protocol_ready"] is True
    assert summary["genuine_blocker_work_package_registry_ready"] is True
    assert summary["validation_blocker_resolution_readiness_ready"] is True
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
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["forbidden_repo_output_count"] == 0
    assert summary["alpha28_freeze_hash_valid"] is True
    assert summary["alpha27_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["economic_validation_status"] == (
        "genuine_validation_blockers_preregistered_no_resolution_execution"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
    assert summary["development_next_phase"] == 33
    assert summary["phase32_closure_status"] == (
        "closed_genuine_validation_blocker_resolution_plan_preregistered_no_execution"
    )


def test_show_phase32_genuine_blocker_resolution_plan_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase32_genuine_blocker_resolution_plan_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase=32" in result.stdout
    assert "result=passed" in result.stdout
    assert (
        "phase32_closure_status="
        "closed_genuine_validation_blocker_resolution_plan_preregistered_no_execution"
    ) in result.stdout
