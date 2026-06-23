from __future__ import annotations

from business_cycle.shadow_model.formal_decision_contract import (
    load_formal_decision_model_contract,
    summarize_formal_decision_model_contract,
)


def test_formal_decision_contract_is_preregistered_and_disabled() -> None:
    summary = summarize_formal_decision_model_contract()

    assert summary["formal_decision_contract_ready"] is True
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


def test_contract_blocks_forbidden_phase_decision_inputs() -> None:
    contract = load_formal_decision_model_contract()

    prohibited = set(contract["prohibited_inputs"])
    assert "scenario_id" in prohibited
    assert "expected_historical_label" in prohibited
    assert "nber_date" in prohibited
    assert "portfolio_return" in prohibited
    assert contract["raw_observation_only_rule"][
        "smoothing_alone_phase_support_allowed"
    ] is False
    assert contract["raw_observation_only_rule"][
        "raw_direction_as_turning_point_allowed"
    ] is False
    assert contract["major_group_completeness_requirements"][
        "modern_extensions_may_not_replace_book_core"
    ] is True
    assert contract["major_group_completeness_requirements"][
        "supporting_roles_may_not_replace_core"
    ] is True


def test_contract_does_not_define_weights_thresholds_or_role_votes() -> None:
    contract = load_formal_decision_model_contract()
    guards = contract["disabled_runtime_guards"]

    assert guards["numeric_weight_added"] is False
    assert guards["arbitrary_threshold_added"] is False
    assert guards["role_count_voting_added"] is False
    assert contract["mixed_evidence_rule"]["role_count_voting_allowed"] is False
