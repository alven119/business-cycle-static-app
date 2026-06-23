from __future__ import annotations

from business_cycle.audits.phase13_formal_decision_contract_closure import (
    summarize_phase13_formal_decision_contract_closure,
)


def main() -> None:
    summary = summarize_phase13_formal_decision_contract_closure()
    for key in (
        "phase",
        "phase_id",
        "north_star_alignment_status",
        "semantic_drift_count",
        "formal_decision_contract_ready",
        "candidate_precondition_profile_ready",
        "candidate_input_eligibility_rule_count",
        "phase_presence_transition_separation_valid",
        "abstention_propagation_ready",
        "contradictory_evidence_rule_ready",
        "mixed_evidence_rule_ready",
        "unavailable_evidence_rule_ready",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "alpha9_freeze_hash_valid",
        "alpha8_parent_preserved",
        "qa12_freeze_unchanged",
        "formal_decision_model_ready",
        "candidate_capability_ready",
        "economic_validation_status",
        "data_only_model_economically_validated",
        "independent_validation_ready",
        "holdout_registered",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "development_next_phase",
        "prospective_track_next_action",
        "phase13_closure_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
