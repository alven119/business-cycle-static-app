from __future__ import annotations

from business_cycle.audits.phase13_formal_decision_contract_closure import (
    summarize_phase13_formal_decision_contract_closure,
)


def test_phase13_formal_decision_contract_closure_passes() -> None:
    summary = summarize_phase13_formal_decision_contract_closure()

    assert summary["result"] == "passed"
    assert summary["formal_decision_contract_ready"] is True
    assert summary["candidate_precondition_profile_ready"] is True
    assert summary["candidate_input_eligibility_rule_count"] > 0
    assert summary["phase_presence_transition_separation_valid"] is True
    assert summary["abstention_propagation_ready"] is True
    assert summary["contradictory_evidence_rule_ready"] is True
    assert summary["mixed_evidence_rule_ready"] is True
    assert summary["unavailable_evidence_rule_ready"] is True
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["alpha9_freeze_hash_valid"] is True
    assert summary["alpha8_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["formal_decision_model_ready"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["economic_validation_status"] == "not_started"
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
    assert summary["development_next_phase"] == 14
    assert summary["phase13_closure_status"] == (
        "closed_formal_decision_contract_preregistered_candidate_output_disabled"
    )
