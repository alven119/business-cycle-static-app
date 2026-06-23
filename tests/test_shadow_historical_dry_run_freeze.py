from __future__ import annotations

from business_cycle.audits.shadow_historical_dry_run_freeze import (
    summarize_shadow_historical_dry_run_freeze,
)


def test_alpha16_historical_dry_run_freeze_is_valid() -> None:
    summary = summarize_shadow_historical_dry_run_freeze()

    assert summary["historical_dry_run_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha16"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha15"
    assert summary["alpha16_freeze_hash_valid"] is True
    assert summary["alpha15_parent_preserved"] is True
    assert summary["parent_freeze_present"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["historical_validation_dry_run_executed"] is True
    assert summary["result_artifacts_only"] is True
    assert summary["locked_execution_plan_used"] is True
    assert summary["label_blind_execution_verified"] is True
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["model_execution_count"] == 5
    assert summary["real_historical_validation_executed"] is True
    assert summary["historical_validation_result_count"] == 5
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["holdout_registered"] is False
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
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
        "dry_run_results_generated_no_metrics"
    )
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
