from __future__ import annotations

from business_cycle.audits.shadow_validation_execution_readiness_freeze import (
    summarize_shadow_validation_execution_readiness_freeze,
)


def test_alpha15_validation_execution_readiness_freeze_is_valid() -> None:
    summary = summarize_shadow_validation_execution_readiness_freeze()

    assert summary["validation_execution_readiness_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha15"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha14"
    assert summary["freeze_type"] == (
        "historical_validation_execution_readiness_gate_no_execution"
    )
    assert summary["alpha15_freeze_hash_valid"] is True
    assert summary["alpha14_parent_preserved"] is True
    assert summary["parent_freeze_present"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["execution_readiness_gated"] is True
    assert summary["execution_allowed_in_this_phase"] is False
    assert summary["model_execution_count"] == 0
    assert summary["real_historical_validation_executed"] is False
    assert summary["historical_validation_result_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["holdout_registered"] is False
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["economic_validation_status"] == "not_started"
    assert summary["prospective_registry_record_count"] == 0
    assert summary["prospective_registry_write_attempt_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False


def test_alpha15_parent_and_readiness_are_ready() -> None:
    summary = summarize_shadow_validation_execution_readiness_freeze()

    assert summary["parent_freeze"]["freeze_id"] == "book_faithful_shadow_v2_alpha14"
    assert summary["parent_freeze"]["historical_input_readiness_freeze_ready"] is True
    assert summary["historical_validation_execution_readiness_contract_ready"] is True
    assert summary["historical_validation_execution_plan_ready"] is True
    assert summary["result_artifact_contract_ready"] is True
