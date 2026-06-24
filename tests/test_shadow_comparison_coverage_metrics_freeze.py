from __future__ import annotations

from business_cycle.audits.shadow_comparison_coverage_metrics_freeze import (
    summarize_shadow_comparison_coverage_metrics_freeze,
)


def test_alpha19_comparison_coverage_metrics_freeze_is_valid() -> None:
    summary = summarize_shadow_comparison_coverage_metrics_freeze()

    assert summary["comparison_coverage_metrics_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha19"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha18"
    assert summary["alpha19_freeze_hash_valid"] is True
    assert summary["alpha18_parent_preserved"] is True
    assert summary["parent_freeze_present"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["comparison_coverage_metrics_contract_ready"] is True
    assert summary["comparison_coverage_metrics_runtime_ready"] is True
    assert summary["comparison_coverage_metrics_registry_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["label_provenance_verified_count"] == 5
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["comparison_coverage_metric_count"] == 14
    assert summary["metric_computation_enabled"] is True
    assert summary["metric_computation_scope"] == "comparison_coverage_only"
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["prohibited_metric_field_count"] == 0
    assert summary["predicted_label_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["holdout_registered"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["prospective_registry_write_attempt_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["economic_validation_status"] == (
        "comparison_coverage_metrics_computed_no_accuracy"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
