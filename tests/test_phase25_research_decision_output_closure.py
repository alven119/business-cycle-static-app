from __future__ import annotations

from business_cycle.audits.phase25_research_decision_output_closure import (
    summarize_phase25_research_decision_output_closure,
)


def test_phase25_research_decision_output_closure_passes() -> None:
    summary = summarize_phase25_research_decision_output_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["research_decision_output_artifact_contract_ready"] is True
    assert summary["research_decision_output_runtime_ready"] is True
    assert summary["research_decision_output_registry_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["research_decision_output_count"] == 5
    assert summary["output_mode_research_only_count"] == 5
    assert summary["predicted_label_output_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_scope"] == "none"
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_artifact_field_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["alpha21_freeze_hash_valid"] is True
    assert summary["alpha20_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["economic_validation_status"] == (
        "research_decision_outputs_generated_no_predicted_labels"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
    assert summary["development_next_phase"] == 26
    assert summary["prospective_track_next_action"] == "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
    assert summary["phase25_closure_status"] == (
        "closed_research_decision_outputs_generated_no_predicted_labels_or_metrics"
    )
