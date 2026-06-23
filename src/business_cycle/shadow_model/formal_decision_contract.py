"""Phase 13 formal decision model contract preregistration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_FORMAL_DECISION_CONTRACT_PATH = Path(
    "specs/common/formal_decision_model_contract.yaml"
)


REQUIRED_CONTRACT_FIELDS = {
    "model_layer_id",
    "allowed_inputs",
    "prohibited_inputs",
    "phase_presence_requirements",
    "transition_watch_requirements",
    "transition_confirmation_requirements",
    "major_group_completeness_requirements",
    "abstention_propagation_rule",
    "contradictory_evidence_rule",
    "mixed_evidence_rule",
    "unavailable_evidence_rule",
    "raw_observation_only_rule",
    "temporal_integrity_rule",
    "same_as_of_requirement",
    "data_mode_requirement",
    "provenance_requirement",
    "candidate_input_eligibility_rule",
    "candidate_output_rule",
    "readiness_gates",
    "disabled_runtime_guards",
}


def load_formal_decision_model_contract(
    path: str | Path = DEFAULT_FORMAL_DECISION_CONTRACT_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "formal_decision_model_contract"
    ]


def summarize_formal_decision_model_contract(
    path: str | Path = DEFAULT_FORMAL_DECISION_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_formal_decision_model_contract(path)
    missing = sorted(REQUIRED_CONTRACT_FIELDS - set(contract))
    output_rule = contract["candidate_output_rule"]
    guards = contract["disabled_runtime_guards"]
    readiness = contract["readiness_gates"]
    phase_presence_transition_separation_valid = _separation_valid(contract)
    summary = {
        "phase": "13",
        "model_layer_id": contract["model_layer_id"],
        "contract_status": contract["contract_status"],
        "allowed_input_count": len(contract["allowed_inputs"]),
        "prohibited_input_count": len(contract["prohibited_inputs"]),
        "phase_presence_requirement_count": len(
            contract["phase_presence_requirements"]
        ),
        "transition_watch_requirement_count": len(
            contract["transition_watch_requirements"]
        ),
        "transition_confirmation_requirement_count": len(
            contract["transition_confirmation_requirements"]
        ),
        "candidate_input_eligibility_rule_count": len(
            contract["candidate_input_eligibility_rule"]["rules"]
        ),
        "candidate_precondition_profile_count": len(
            contract["candidate_precondition_profiles"]
        ),
        "missing_required_contract_field_count": len(missing),
        "phase_presence_transition_separation_valid": (
            phase_presence_transition_separation_valid
        ),
        "abstention_propagation_ready": (
            contract["abstention_propagation_rule"]["incomplete_required_group_status"]
            == "abstain"
        ),
        "contradictory_evidence_rule_ready": (
            contract["contradictory_evidence_rule"][
                "contradictory_evidence_may_not_be_averaged_away"
            ]
            is True
        ),
        "mixed_evidence_rule_ready": (
            contract["mixed_evidence_rule"]["role_count_voting_allowed"] is False
        ),
        "unavailable_evidence_rule_ready": (
            contract["unavailable_evidence_rule"]["neutral_substitution_allowed"]
            is False
        ),
        "raw_observation_only_rule_ready": (
            contract["raw_observation_only_rule"][
                "smoothing_alone_phase_support_allowed"
            ]
            is False
            and contract["raw_observation_only_rule"][
                "raw_direction_as_turning_point_allowed"
            ]
            is False
        ),
        "temporal_integrity_rule_ready": (
            contract["temporal_integrity_rule"]["causal_only"] is True
            and contract["temporal_integrity_rule"]["future_data_allowed"] is False
            and contract["temporal_integrity_rule"]["mixed_data_mode_allowed"]
            is False
        ),
        "same_as_of_requirement_ready": (
            contract["same_as_of_requirement"]["required"] is True
        ),
        "data_mode_requirement_ready": (
            contract["data_mode_requirement"][
                "strict_and_revised_must_be_separated"
            ]
            is True
        ),
        "provenance_requirement_ready": all(
            value is True for value in contract["provenance_requirement"].values()
        ),
        "numeric_weight_added_count": int(guards["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(guards["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(guards["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(guards["historical_tuning_used"]),
        "candidate_selection_enabled": output_rule["candidate_selection_enabled"],
        "candidate_phase_emitted": output_rule[
            "candidate_phase_emission_allowed"
        ],
        "current_phase_emitted": output_rule["current_phase_emission_allowed"],
        "selected_candidate_phase_field_allowed": output_rule[
            "selected_candidate_phase_field_allowed"
        ],
        "current_phase_field_allowed": output_rule["current_phase_field_allowed"],
        "production_import_allowed": guards["production_import_allowed"],
        "public_output_allowed": guards["public_output_allowed"],
        "data_backtests_write_allowed": guards["data_backtests_write_allowed"],
        "data_prospective_write_allowed": guards["data_prospective_write_allowed"],
        "prospective_registry_write_allowed": guards[
            "prospective_registry_write_allowed"
        ],
        "missing_required_contract_fields": missing,
    }
    summary["formal_decision_contract_ready"] = (
        summary["missing_required_contract_field_count"] == 0
        and readiness["formal_decision_contract_ready"] is True
        and summary["candidate_input_eligibility_rule_count"]
        >= readiness["candidate_input_eligibility_rule_count_minimum"]
        and summary["phase_presence_transition_separation_valid"] is True
        and summary["abstention_propagation_ready"] is True
        and summary["contradictory_evidence_rule_ready"] is True
        and summary["mixed_evidence_rule_ready"] is True
        and summary["unavailable_evidence_rule_ready"] is True
        and summary["raw_observation_only_rule_ready"] is True
        and summary["temporal_integrity_rule_ready"] is True
        and summary["same_as_of_requirement_ready"] is True
        and summary["data_mode_requirement_ready"] is True
        and summary["provenance_requirement_ready"] is True
        and summary["numeric_weight_added_count"] == 0
        and summary["arbitrary_threshold_added_count"] == 0
        and summary["role_count_voting_added_count"] == 0
        and summary["historical_tuning_leakage_count"] == 0
        and summary["candidate_selection_enabled"] is False
        and summary["candidate_phase_emitted"] is False
        and summary["current_phase_emitted"] is False
        and summary["production_import_allowed"] is False
        and summary["public_output_allowed"] is False
        and summary["data_backtests_write_allowed"] is False
        and summary["data_prospective_write_allowed"] is False
        and summary["prospective_registry_write_allowed"] is False
    )
    return summary


def _separation_valid(contract: dict[str, Any]) -> bool:
    watch_rules = contract["transition_watch_requirements"]
    confirmation_rules = contract["transition_confirmation_requirements"]
    raw_rule = contract["raw_observation_only_rule"]
    completeness = contract["major_group_completeness_requirements"]
    return (
        watch_rules["boom_ending_watch"]["cannot_satisfy_phase_presence"] is True
        and watch_rules["recession_watch"][
            "cannot_satisfy_recession_confirmation"
        ]
        is True
        and watch_rules["recovery_watch"]["cannot_satisfy_formal_recovery"]
        is True
        and confirmation_rules["recession_confirmation"][
            "watch_evidence_is_insufficient"
        ]
        is True
        and confirmation_rules["trough_confirmation"][
            "policy_financial_only_is_insufficient"
        ]
        is True
        and raw_rule["smoothing_alone_phase_support_allowed"] is False
        and raw_rule["raw_direction_as_turning_point_allowed"] is False
        and completeness["supporting_roles_may_not_replace_core"] is True
        and completeness["modern_extensions_may_not_replace_book_core"] is True
    )
