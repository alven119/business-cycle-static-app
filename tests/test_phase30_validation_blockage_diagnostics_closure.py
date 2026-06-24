from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase30_validation_blockage_diagnostics_closure import (
    summarize_phase30_validation_blockage_diagnostics_closure,
)


def test_phase30_validation_blockage_diagnostics_closure_passes() -> None:
    summary = summarize_phase30_validation_blockage_diagnostics_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["product_capabilities_advanced"] == [
        "C3_EXPLAINABILITY_AND_ATTRIBUTION",
        "C5_HISTORICAL_REPLAY_AND_BACKTEST",
        "C6_SAFE_OUTPUT_GOVERNANCE",
        "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
        "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
    ]
    assert summary["web_surfaces_advanced"] == [
        "W6_HISTORICAL_REPLAY",
        "W7_DATA_LINEAGE",
        "W8_BACKTEST_RESEARCH",
        "W13_MODEL_GOVERNANCE",
    ]
    assert summary["semantic_drift_count"] == 0
    assert summary["historical_validation_blockage_diagnostics_contract_ready"] is True
    assert summary["historical_validation_blockage_diagnostics_runtime_ready"] is True
    assert summary["scenario_validation_trace_contract_ready"] is True
    assert summary["scenario_validation_trace_runtime_ready"] is True
    assert summary["research_artifact_explorer_contract_ready"] is True
    assert summary["research_artifact_explorer_runtime_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_trace_count"] == 5
    assert summary["blockage_diagnostic_scenario_count"] == 5
    assert summary["blocked_scenario_count"] == 5
    assert summary["blockage_reason_summary_ready"] is True
    assert summary["remediation_plan_registry_ready"] is True
    assert summary["remediation_action_executed"] is False
    assert summary["rule_modified_count"] == 0
    assert summary["mapping_rule_modified_count"] == 0
    assert summary["threshold_modified_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["new_accuracy_metric_computed_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_scope"] == "diagnostic_summary_only"
    assert summary["backtest_execution_enabled"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_explorer_field_count"] == 0
    assert summary["explorer_written_to_public_count"] == 0
    assert summary["forbidden_repo_output_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["alpha26_freeze_hash_valid"] is True
    assert summary["alpha25_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["economic_validation_status"] == (
        "historical_validation_blockage_diagnostics_generated_no_remediation_or_performance"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
    assert summary["development_next_phase"] == 31
    assert summary["phase30_closure_status"] == (
        "closed_validation_blockage_diagnostics_and_research_explorer_generated_no_remediation"
    )


def test_show_phase30_validation_blockage_diagnostics_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase30_validation_blockage_diagnostics_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase=30" in result.stdout
    assert "result=passed" in result.stdout
    assert (
        "phase30_closure_status="
        "closed_validation_blockage_diagnostics_and_research_explorer_generated_no_remediation"
    ) in result.stdout
