from __future__ import annotations

from business_cycle.audits.phase29_historical_accuracy_metrics_closure import (
    summarize_phase29_historical_accuracy_metrics_closure,
)


def test_phase29_historical_accuracy_metrics_closure_passes() -> None:
    summary = summarize_phase29_historical_accuracy_metrics_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["historical_accuracy_metric_artifact_contract_ready"] is True
    assert summary["historical_accuracy_metric_runtime_ready"] is True
    assert summary["historical_accuracy_metric_readiness_ready"] is True
    assert summary["preregistered_metric_registry_used"] is True
    assert summary["scenario_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["comparable_scenario_count"] == 0
    assert summary["non_comparable_scenario_count"] == 0
    assert summary["abstained_scenario_count"] == 0
    assert summary["blocked_scenario_count"] == 5
    assert summary["taxonomy_mismatch_count"] == 0
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
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["forbidden_repo_output_count"] == 0
    assert summary["alpha25_freeze_hash_valid"] is True
    assert summary["alpha24_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["economic_validation_status"] == (
        "historical_accuracy_metrics_computed_research_only_no_performance"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
    assert summary["development_next_phase"] == 30
    assert summary["phase29_closure_status"] == (
        "closed_historical_accuracy_metrics_computed_research_only_no_economic_performance"
    )
