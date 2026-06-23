from __future__ import annotations

from business_cycle.audits.shadow_historical_manifest_freeze import (
    summarize_shadow_historical_manifest_freeze,
)


def test_alpha13_historical_manifest_freeze_is_valid() -> None:
    summary = summarize_shadow_historical_manifest_freeze()

    assert summary["historical_manifest_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha13"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha12"
    assert summary["freeze_type"] == (
        "historical_validation_manifest_preregistration_no_execution"
    )
    assert summary["alpha13_freeze_hash_valid"] is True
    assert summary["alpha12_parent_preserved"] is True
    assert summary["parent_freeze_present"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["manifest_preregistered"] is True
    assert summary["validation_label_policy_preregistered"] is True
    assert summary["real_historical_validation_executed"] is False
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


def test_alpha13_parent_and_phase17_artifacts_are_ready() -> None:
    summary = summarize_shadow_historical_manifest_freeze()

    assert summary["parent_freeze"]["freeze_id"] == "book_faithful_shadow_v2_alpha12"
    assert summary["parent_freeze"]["validation_harness_freeze_ready"] is True
    assert summary["historical_validation_manifest_contract_ready"] is True
    assert summary["historical_validation_scenario_manifest_ready"] is True
    assert summary["validation_label_policy_ready"] is True
    assert summary["historical_validation_readiness_ready"] is True
