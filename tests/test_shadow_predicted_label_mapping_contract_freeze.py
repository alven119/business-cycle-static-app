from __future__ import annotations

from business_cycle.audits.shadow_predicted_label_mapping_contract_freeze import (
    summarize_shadow_predicted_label_mapping_contract_freeze,
)


def test_alpha22_predicted_label_mapping_contract_freeze_is_valid() -> None:
    summary = summarize_shadow_predicted_label_mapping_contract_freeze()

    assert summary["predicted_label_mapping_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha22"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha21"
    assert summary["alpha22_freeze_hash_valid"] is True
    assert summary["alpha21_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["predicted_label_mapping_contract_ready"] is True
    assert summary["predicted_label_mapping_readiness_ready"] is True
    assert summary["research_decision_state_taxonomy_ready"] is True
    assert summary["offline_predicted_label_taxonomy_ready"] is True
    assert summary["mapping_rule_count"] > 0
    assert summary["predicted_label_output_count"] == 0
    assert summary["predicted_label_artifact_count"] == 0
    assert summary["label_comparison_executed"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["economic_validation_status"] == (
        "predicted_label_mapping_preregistered_no_emission"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
