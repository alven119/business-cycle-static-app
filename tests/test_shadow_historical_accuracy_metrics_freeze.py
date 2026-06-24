from __future__ import annotations

from business_cycle.audits.shadow_historical_accuracy_metrics_freeze import (
    summarize_shadow_historical_accuracy_metrics_freeze,
)


def test_alpha25_historical_accuracy_metrics_freeze_is_valid() -> None:
    summary = summarize_shadow_historical_accuracy_metrics_freeze()

    assert summary["historical_accuracy_metrics_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha25"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha24"
    assert summary["alpha25_freeze_hash_valid"] is True
    assert summary["alpha24_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["scenario_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is True
    assert summary["metric_computation_scope"] == "historical_accuracy_only"
    assert summary["backtest_execution_enabled"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["mapping_rule_modified_after_comparison_count"] == 0
    assert summary["threshold_modified_after_metric_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_metric_field_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["prospective_registry_write_attempt_count"] == 0
    assert summary["forbidden_repo_output_count"] == 0
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["production_book_fidelity_ready"] is False
    assert summary["economic_validation_status"] == (
        "historical_accuracy_metrics_computed_research_only_no_performance"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
