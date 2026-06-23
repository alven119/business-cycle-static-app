"""Phase 13 candidate precondition diagnostics with candidate output disabled."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from business_cycle.shadow_model.formal_decision_contract import (
    DEFAULT_FORMAL_DECISION_CONTRACT_PATH,
    load_formal_decision_model_contract,
    summarize_formal_decision_model_contract,
)
from business_cycle.shadow_model.major_group_evidence import (
    build_major_group_phase_evidence_rows,
)


def build_candidate_precondition_profiles(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
    contract_path: str | Path = DEFAULT_FORMAL_DECISION_CONTRACT_PATH,
) -> list[dict[str, Any]]:
    contract = load_formal_decision_model_contract(contract_path)
    groups = {
        (row["phase_or_layer"], row["major_group_id"]): row
        for row in build_major_group_phase_evidence_rows(
            as_of=as_of,
            data_mode=data_mode,
        )
    }
    output_rule = contract["candidate_output_rule"]
    profiles: list[dict[str, Any]] = []
    for profile in contract["candidate_precondition_profiles"]:
        required = profile["required_major_groups"]
        group_rows = [
            groups.get((profile["phase_presence_layer"], major_group_id))
            for major_group_id in required
        ]
        missing = [
            major_group_id
            for major_group_id, row in zip(required, group_rows)
            if row is None
        ]
        incomplete = [
            row["major_group_id"]
            for row in group_rows
            if row is not None
            and row["group_evidence_status"]
            in {"incomplete", "unavailable", "temporal_abstention", "rule_unresolved"}
        ]
        mixed_or_contradictory = [
            row["major_group_id"]
            for row in group_rows
            if row is not None
            and row["group_evidence_status"] in {"mixed", "contradictory"}
        ]
        provenance_complete = not missing
        precondition_met = (
            not missing
            and not incomplete
            and not mixed_or_contradictory
            and provenance_complete
        )
        blockers = _blockers(
            missing=missing,
            incomplete=incomplete,
            mixed_or_contradictory=mixed_or_contradictory,
            candidate_output_disabled=not output_rule[
                "candidate_phase_emission_allowed"
            ],
        )
        profiles.append(
            {
                "profile_id": profile["profile_id"],
                "diagnostic_phase_id": profile["diagnostic_phase_id"],
                "phase_presence_layer": profile["phase_presence_layer"],
                "required_major_groups": required,
                "major_group_statuses": [
                    {
                        "major_group_id": row["major_group_id"],
                        "group_evidence_status": row["group_evidence_status"],
                        "evaluable_core_role_count": row[
                            "evaluable_core_role_count"
                        ],
                        "required_core_role_count": len(
                            row["required_core_role_ids"]
                        ),
                    }
                    for row in group_rows
                    if row is not None
                ],
                "required_major_group_count": len(required),
                "missing_major_group_count": len(missing),
                "incomplete_required_major_group_count": len(incomplete),
                "mixed_or_contradictory_group_count": len(mixed_or_contradictory),
                "precondition_evidence_complete": precondition_met,
                "candidate_input_eligibility_diagnostic": (
                    "complete_but_output_disabled"
                    if precondition_met
                    else "incomplete_or_abstained"
                ),
                "candidate_input_eligible": False,
                "candidate_selection_enabled": output_rule[
                    "candidate_selection_enabled"
                ],
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
                "readiness_blockers": blockers,
                "provenance_complete": provenance_complete,
            }
        )
    return profiles


def summarize_candidate_precondition_profiles() -> dict[str, Any]:
    contract_summary = summarize_formal_decision_model_contract()
    profiles = build_candidate_precondition_profiles()
    candidate_output_fields = sum(
        any(key in row for key in ("candidate_phase", "selected_candidate_phase", "current_phase"))
        for row in profiles
    )
    return {
        "phase": "13",
        "candidate_precondition_profile_ready": (
            contract_summary["formal_decision_contract_ready"]
            and len(profiles)
            == contract_summary["candidate_precondition_profile_count"]
            and candidate_output_fields == 0
            and all(row["candidate_input_eligible"] is False for row in profiles)
            and all(row["candidate_selection_enabled"] is False for row in profiles)
            and all(row["candidate_phase_emitted"] is False for row in profiles)
            and all(row["current_phase_emitted"] is False for row in profiles)
        ),
        "candidate_precondition_profile_count": len(profiles),
        "candidate_input_eligibility_rule_count": contract_summary[
            "candidate_input_eligibility_rule_count"
        ],
        "precondition_evidence_complete_profile_count": sum(
            row["precondition_evidence_complete"] for row in profiles
        ),
        "candidate_input_eligible_profile_count": sum(
            row["candidate_input_eligible"] for row in profiles
        ),
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "candidate_output_field_count": candidate_output_fields,
        "missing_major_group_count": sum(
            row["missing_major_group_count"] for row in profiles
        ),
        "incomplete_required_major_group_count": sum(
            row["incomplete_required_major_group_count"] for row in profiles
        ),
        "mixed_or_contradictory_group_count": sum(
            row["mixed_or_contradictory_group_count"] for row in profiles
        ),
        "numeric_weight_added_count": contract_summary[
            "numeric_weight_added_count"
        ],
        "arbitrary_threshold_added_count": contract_summary[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": contract_summary[
            "role_count_voting_added_count"
        ],
        "historical_tuning_leakage_count": contract_summary[
            "historical_tuning_leakage_count"
        ],
        "profiles": profiles,
    }


def _blockers(
    *,
    missing: list[str],
    incomplete: list[str],
    mixed_or_contradictory: list[str],
    candidate_output_disabled: bool,
) -> list[str]:
    blockers: list[str] = []
    blockers.extend(f"missing_major_group:{item}" for item in missing)
    blockers.extend(f"incomplete_required_major_group:{item}" for item in incomplete)
    blockers.extend(
        f"mixed_or_contradictory_major_group:{item}"
        for item in mixed_or_contradictory
    )
    if candidate_output_disabled:
        blockers.append("candidate_output_disabled_by_phase13_contract")
    return sorted(blockers)
