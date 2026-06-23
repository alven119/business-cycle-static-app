from __future__ import annotations

from business_cycle.audits.shadow_decision_contract_freeze import (
    summarize_shadow_decision_contract_freeze,
)


def test_alpha9_decision_contract_freeze_is_valid() -> None:
    summary = summarize_shadow_decision_contract_freeze()

    assert summary["decision_contract_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha9"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha8"
    assert summary["alpha9_freeze_hash_valid"] is True
    assert summary["alpha8_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["holdout_registered"] is False


def test_alpha9_parent_is_alpha8_and_contracts_are_ready() -> None:
    summary = summarize_shadow_decision_contract_freeze()

    assert summary["parent_freeze"]["freeze_id"] == "book_faithful_shadow_v2_alpha8"
    assert summary["parent_freeze"]["gap_resolution_freeze_ready"] is True
    assert summary["formal_decision_contract_ready"] is True
    assert summary["candidate_precondition_profile_ready"] is True
