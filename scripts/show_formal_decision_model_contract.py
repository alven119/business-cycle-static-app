from __future__ import annotations

from business_cycle.shadow_model.candidate_precondition_profiles import (
    summarize_candidate_precondition_profiles,
)
from business_cycle.shadow_model.formal_decision_contract import (
    summarize_formal_decision_model_contract,
)


def main() -> None:
    contract = summarize_formal_decision_model_contract()
    profiles = summarize_candidate_precondition_profiles()
    merged = {**contract, **profiles}
    for key in (
        "phase",
        "model_layer_id",
        "contract_status",
        "formal_decision_contract_ready",
        "candidate_precondition_profile_ready",
        "allowed_input_count",
        "prohibited_input_count",
        "phase_presence_requirement_count",
        "transition_watch_requirement_count",
        "transition_confirmation_requirement_count",
        "candidate_input_eligibility_rule_count",
        "candidate_precondition_profile_count",
        "phase_presence_transition_separation_valid",
        "abstention_propagation_ready",
        "contradictory_evidence_rule_ready",
        "mixed_evidence_rule_ready",
        "unavailable_evidence_rule_ready",
        "raw_observation_only_rule_ready",
        "temporal_integrity_rule_ready",
        "same_as_of_requirement_ready",
        "data_mode_requirement_ready",
        "provenance_requirement_ready",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "candidate_output_field_count",
    ):
        value = merged[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
