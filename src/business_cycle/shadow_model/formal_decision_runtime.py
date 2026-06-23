"""Phase 14 non-emitting formal decision runtime diagnostics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
)
from business_cycle.shadow_model.candidate_precondition_profiles import (
    build_candidate_precondition_profiles,
    summarize_candidate_precondition_profiles,
)
from business_cycle.shadow_model.formal_decision_contract import (
    load_formal_decision_model_contract,
    summarize_formal_decision_model_contract,
)


DEFAULT_RUNTIME_CONTRACT_PATH = Path(
    "specs/common/non_emitting_decision_runtime_contract.yaml"
)
RUNTIME_VERSION = "phase14_non_emitting_decision_runtime_v1"
MODEL_ID = "book_faithful_shadow_v2_alpha10"
FREEZE_ID = "book_faithful_shadow_v2_alpha10"


def load_non_emitting_decision_runtime_contract(
    path: str | Path = DEFAULT_RUNTIME_CONTRACT_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "non_emitting_decision_runtime_contract"
    ]


def run_formal_decision_runtime_diagnostics(
    *,
    as_of: str,
    data_mode: str,
    runtime_contract_path: str | Path = DEFAULT_RUNTIME_CONTRACT_PATH,
) -> dict[str, Any]:
    runtime_contract = load_non_emitting_decision_runtime_contract(
        runtime_contract_path
    )
    decision_contract = load_formal_decision_model_contract()
    profiles = build_candidate_precondition_profiles(as_of=as_of, data_mode=data_mode)
    precondition_results = [_safe_precondition_result(row) for row in profiles]
    blocked_reason_codes = _blocked_reason_codes(profiles)
    output = {
        "runtime_version": runtime_contract["runtime_version"],
        "as_of": as_of,
        "data_mode": data_mode,
        "model_id": runtime_contract["model_id"],
        "freeze_id": runtime_contract["freeze_id"],
        "readiness_label": runtime_contract["runtime_status"],
        "allowed_uses": [
            "decision_readiness_diagnostics",
            "contract_enforcement_audit",
        ],
        "prohibited_uses": [
            "candidate_phase_output",
            "current_phase_decision",
            "portfolio_action",
            "production_dashboard_output",
            "backtest_performance",
        ],
        "trust_metadata": {
            "model_id": runtime_contract["model_id"],
            "freeze_id": runtime_contract["freeze_id"],
            "parent_freeze_id": runtime_contract["parent_freeze_id"],
            "contract_version": decision_contract["version"],
            "runtime_version": runtime_contract["runtime_version"],
            "as_of": as_of,
            "data_mode": data_mode,
            "provenance_complete": True,
        },
        "evaluated_phase_or_layer_count": len(
            {row["phase_presence_layer"] for row in profiles}
        ),
        "precondition_check_results": precondition_results,
        "abstention_reasons": _abstention_reasons(profiles),
        "contradictory_evidence_reasons": _contradictory_evidence_reasons(
            profiles
        ),
        "mixed_evidence_reasons": _mixed_evidence_reasons(profiles),
        "unavailable_evidence_reasons": _unavailable_evidence_reasons(profiles),
        "raw_observation_only_reasons": _raw_observation_only_reasons(),
        "blocked_reason_codes": blocked_reason_codes,
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    _assert_no_forbidden_outputs(output, runtime_contract["forbidden_outputs"])
    return output


def summarize_formal_decision_runtime(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
) -> dict[str, Any]:
    runtime_contract = load_non_emitting_decision_runtime_contract()
    diagnostics = run_formal_decision_runtime_diagnostics(
        as_of=as_of,
        data_mode=data_mode,
    )
    contract = summarize_formal_decision_model_contract()
    profiles = summarize_candidate_precondition_profiles()
    forbidden_counts = _forbidden_output_counts(
        diagnostics,
        runtime_contract["forbidden_outputs"],
    )
    executed = _runtime_rule_execution_flags(diagnostics)
    return {
        "phase": "14",
        "non_emitting_decision_runtime_ready": (
            contract["formal_decision_contract_ready"]
            and profiles["candidate_precondition_profile_ready"]
            and all(value == 0 for value in forbidden_counts.values())
            and diagnostics["candidate_selection_enabled"] is False
            and diagnostics["candidate_phase_emitted"] is False
            and diagnostics["current_phase_emitted"] is False
        ),
        "formal_decision_contract_enforced": contract[
            "formal_decision_contract_ready"
        ],
        "evaluated_precondition_rule_count": len(
            runtime_contract["enforced_rules"]
        ),
        "phase_presence_transition_separation_valid": contract[
            "phase_presence_transition_separation_valid"
        ],
        "watch_confirmation_separation_valid": _watch_confirmation_valid(
            runtime_contract
        ),
        "abstention_propagation_executed": executed[
            "abstention_propagation_executed"
        ],
        "contradictory_evidence_rule_executed": executed[
            "contradictory_evidence_rule_executed"
        ],
        "mixed_evidence_rule_executed": executed["mixed_evidence_rule_executed"],
        "unavailable_evidence_rule_executed": executed[
            "unavailable_evidence_rule_executed"
        ],
        "raw_observation_only_blocking_executed": executed[
            "raw_observation_only_blocking_executed"
        ],
        "prohibited_decision_output_field_count": forbidden_counts[
            "prohibited_decision_output_field_count"
        ],
        "selected_phase_output_count": forbidden_counts[
            "selected_phase_output_count"
        ],
        "phase_rank_output_count": forbidden_counts["phase_rank_output_count"],
        "phase_score_output_count": forbidden_counts["phase_score_output_count"],
        "numeric_weight_added_count": contract["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": contract[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": contract["role_count_voting_added_count"],
        "historical_tuning_leakage_count": contract[
            "historical_tuning_leakage_count"
        ],
        "candidate_selection_enabled": diagnostics["candidate_selection_enabled"],
        "candidate_phase_emitted": diagnostics["candidate_phase_emitted"],
        "current_phase_emitted": diagnostics["current_phase_emitted"],
        "evaluated_phase_or_layer_count": diagnostics[
            "evaluated_phase_or_layer_count"
        ],
        "blocked_reason_count": len(diagnostics["blocked_reason_codes"]),
        "diagnostics": diagnostics,
    }


def _safe_precondition_result(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile_id": row["profile_id"],
        "diagnostic_phase_id": row["diagnostic_phase_id"],
        "phase_presence_layer": row["phase_presence_layer"],
        "required_major_group_count": row["required_major_group_count"],
        "missing_major_group_count": row["missing_major_group_count"],
        "incomplete_required_major_group_count": row[
            "incomplete_required_major_group_count"
        ],
        "mixed_or_contradictory_group_count": row[
            "mixed_or_contradictory_group_count"
        ],
        "precondition_evidence_complete": row["precondition_evidence_complete"],
        "candidate_input_eligibility_diagnostic": row[
            "candidate_input_eligibility_diagnostic"
        ],
        "candidate_input_eligible": False,
        "readiness_blockers": row["readiness_blockers"],
        "provenance_complete": row["provenance_complete"],
    }


def _blocked_reason_codes(profiles: list[dict[str, Any]]) -> list[str]:
    reasons: set[str] = set()
    for profile in profiles:
        reasons.update(profile["readiness_blockers"])
    reasons.update(_raw_observation_only_reasons())
    return sorted(reasons)


def _abstention_reasons(profiles: list[dict[str, Any]]) -> list[str]:
    return sorted(
        reason
        for profile in profiles
        for reason in profile["readiness_blockers"]
        if reason.startswith(("missing_", "incomplete_", "candidate_output"))
    )


def _contradictory_evidence_reasons(profiles: list[dict[str, Any]]) -> list[str]:
    return sorted(
        reason
        for profile in profiles
        for reason in profile["readiness_blockers"]
        if reason.startswith("mixed_or_contradictory")
    )


def _mixed_evidence_reasons(profiles: list[dict[str, Any]]) -> list[str]:
    return _contradictory_evidence_reasons(profiles)


def _unavailable_evidence_reasons(profiles: list[dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    for profile in profiles:
        for group in profile["major_group_statuses"]:
            if group["group_evidence_status"] == "unavailable":
                reasons.append(
                    f"unavailable_required_major_group:{group['major_group_id']}"
                )
    return sorted(reasons)


def _raw_observation_only_reasons() -> list[str]:
    return sorted(
        f"raw_observation_only:{row['role_id']}"
        for row in build_book_phase_evidence_rule_rows()
        if row["evaluator_status"] == "raw_observation_only"
    )


def _runtime_rule_execution_flags(diagnostics: dict[str, Any]) -> dict[str, bool]:
    return {
        "abstention_propagation_executed": bool(diagnostics["abstention_reasons"]),
        "contradictory_evidence_rule_executed": (
            diagnostics["contradictory_evidence_reasons"] is not None
        ),
        "mixed_evidence_rule_executed": diagnostics["mixed_evidence_reasons"]
        is not None,
        "unavailable_evidence_rule_executed": bool(
            diagnostics["unavailable_evidence_reasons"]
        ),
        "raw_observation_only_blocking_executed": bool(
            diagnostics["raw_observation_only_reasons"]
        ),
    }


def _watch_confirmation_valid(runtime_contract: dict[str, Any]) -> bool:
    rule_ids = {row["rule_id"] for row in runtime_contract["enforced_rules"]}
    return "watch_confirmation_separation_v1" in rule_ids


def _forbidden_output_counts(
    payload: dict[str, Any],
    forbidden_outputs: list[str],
) -> dict[str, int]:
    paths = _find_forbidden_output_paths(payload, set(forbidden_outputs))
    return {
        "prohibited_decision_output_field_count": len(paths),
        "selected_phase_output_count": sum(
            path.endswith(
                (
                    "candidate_phase",
                    "current_phase",
                    "winning_phase",
                    "selected_phase",
                    "selected_candidate_phase",
                )
            )
            for path in paths
        ),
        "phase_rank_output_count": sum(path.endswith("phase_rank") for path in paths),
        "phase_score_output_count": sum(
            path.endswith(("phase_score", "phase_probability", "confidence_score"))
            for path in paths
        ),
    }


def _assert_no_forbidden_outputs(
    payload: dict[str, Any],
    forbidden_outputs: list[str],
) -> None:
    paths = _find_forbidden_output_paths(payload, set(forbidden_outputs))
    if paths:
        joined = ", ".join(paths)
        raise ValueError(f"forbidden decision output fields present: {joined}")


def _find_forbidden_output_paths(
    value: Any,
    forbidden: set[str],
    *,
    prefix: str = "",
) -> list[str]:
    if isinstance(value, dict):
        found: list[str] = []
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in forbidden:
                found.append(path)
            found.extend(_find_forbidden_output_paths(item, forbidden, prefix=path))
        return found
    if isinstance(value, list):
        found = []
        for index, item in enumerate(value):
            path = f"{prefix}[{index}]"
            found.extend(_find_forbidden_output_paths(item, forbidden, prefix=path))
        return found
    return []
