from __future__ import annotations

from business_cycle.audits.shadow_predicted_label_artifact_freeze import (
    summarize_shadow_predicted_label_artifact_freeze,
)


def test_alpha23_predicted_label_artifact_freeze_is_valid() -> None:
    summary = summarize_shadow_predicted_label_artifact_freeze()

    assert summary["predicted_label_artifact_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha23"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha22"
    assert summary["alpha23_freeze_hash_valid"] is True
    assert summary["alpha22_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["scenario_count"] == 5
    assert summary["research_decision_output_count"] == 5
    assert summary["predicted_label_artifact_count"] == 5
    assert summary["predicted_label_output_count"] == 5
    assert summary["predicted_label_provenance_complete_count"] == 5
    assert summary["mapping_contract_hash_verified"] is True
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["label_comparison_executed"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_artifact_field_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["economic_validation_status"] == (
        "predicted_label_artifacts_generated_no_comparison_or_metrics"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
