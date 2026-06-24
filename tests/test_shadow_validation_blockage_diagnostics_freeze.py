from __future__ import annotations

from business_cycle.audits.shadow_validation_blockage_diagnostics_freeze import (
    summarize_shadow_validation_blockage_diagnostics_freeze,
)


def test_alpha26_validation_blockage_diagnostics_freeze_is_valid() -> None:
    summary = summarize_shadow_validation_blockage_diagnostics_freeze()

    assert summary["validation_blockage_diagnostics_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha26"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha25"
    assert summary["alpha26_freeze_hash_valid"] is True
    assert summary["alpha25_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
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
    assert summary["prospective_registry_write_attempt_count"] == 0
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["production_book_fidelity_ready"] is False
    assert summary["economic_validation_status"] == (
        "historical_validation_blockage_diagnostics_generated_no_remediation_or_performance"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
