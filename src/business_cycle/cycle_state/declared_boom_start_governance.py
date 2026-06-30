"""Governed confirmation package for the declared boom start date.

This module prepares the inputs needed to confirm a declared boom start date or
start window. It deliberately does not write the declared registry and does not
infer the current phase from current data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.declared_phase_registry import (
    load_declared_cycle_state,
)
from business_cycle.cycle_state.phase_start_research_assistant import (
    build_phase_start_research_assistant,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GOVERNANCE_SPEC_PATH = (
    ROOT / "specs/common/declared_boom_start_governance.yaml"
)

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_score",
    "phase_rank",
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
}


def build_declared_boom_start_governance(
    *,
    spec_path: str | Path = DEFAULT_GOVERNANCE_SPEC_PATH,
    phase_start_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a research-only governed confirmation artifact."""

    spec = _load_spec(spec_path)
    declared_state = load_declared_cycle_state()
    phase_start_artifact = phase_start_artifact or build_phase_start_research_assistant()
    confirmation_options = _confirmation_options()
    artifact: dict[str, Any] = {
        "governance_id": spec["contract_id"],
        "governance_version": spec["contract_version"],
        "output_mode": "research_only_declared_start_governance",
        "declared_current_phase": declared_state.declared_current_phase,
        "legal_previous_phase": declared_state.legal_previous_phase,
        "legal_next_phase": declared_state.legal_next_phase,
        "declared_phase_start_date_current_value": (
            declared_state.declared_phase_start_date.isoformat()
            if declared_state.declared_phase_start_date is not None
            else None
        ),
        "declared_phase_start_date_status": (
            declared_state.declared_phase_start_date_status
        ),
        "phase_age_status_current_value": declared_state.phase_age_status,
        "governed_confirmation_options": confirmation_options,
        "governed_confirmation_option_count": len(confirmation_options),
        "recommended_confirmation_fields": spec["required_confirmation_fields"],
        "recommended_operator_next_action": (
            "COLLECT_USER_DECLARED_BOOM_START_DATE_OR_WINDOW"
        ),
        "governed_start_date_confirmed": False,
        "user_confirmation_required": True,
        "registry_write_allowed": False,
        "declared_registry_modified": False,
        "registry_write_requires_explicit_future_phase": True,
        "phase_age_used_as_transition_gate": False,
        "phase_age_false_precision_count": _phase_age_false_precision_count(
            declared_state,
        ),
        "phase_start_research_hypothesis_count": phase_start_artifact[
            "hypothesis_count"
        ],
        "phase_start_research_missing_evidence_count": phase_start_artifact[
            "missing_evidence_summary"
        ]["missing_evidence_count"],
        "user_prior_hypothesis_present": phase_start_artifact[
            "user_prior_hypothesis_present"
        ],
        "evidence_based_hypothesis_present": phase_start_artifact[
            "evidence_based_hypothesis_present"
        ],
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "selected_phase_output_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_boom_start_governance_ready_registry_unchanged"
        ),
        "legal_transition_semantics_preserved": True,
        "allowed_uses": [
            "declared_phase_start_review",
            "dashboard_phase_age_context_preparation",
            "future_registry_update_planning",
        ],
        "prohibited_uses": spec["prohibited_outputs"],
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["declared_boom_start_governance_ready"] = _passes(artifact, spec)
    artifact["result"] = (
        "passed" if artifact["declared_boom_start_governance_ready"] else "blocked"
    )
    return artifact


def summarize_declared_boom_start_governance() -> dict[str, Any]:
    """Return the Phase51 start-governance summary."""

    artifact = build_declared_boom_start_governance()
    return {
        "declared_boom_start_governance_ready": artifact[
            "declared_boom_start_governance_ready"
        ],
        "declared_current_phase": artifact["declared_current_phase"],
        "legal_next_phase": artifact["legal_next_phase"],
        "declared_phase_start_date_current_value": artifact[
            "declared_phase_start_date_current_value"
        ],
        "declared_phase_start_date_status": artifact[
            "declared_phase_start_date_status"
        ],
        "phase_age_status_current_value": artifact["phase_age_status_current_value"],
        "governed_confirmation_option_count": artifact[
            "governed_confirmation_option_count"
        ],
        "governed_start_date_confirmed": artifact[
            "governed_start_date_confirmed"
        ],
        "user_confirmation_required": artifact["user_confirmation_required"],
        "registry_write_allowed": artifact["registry_write_allowed"],
        "declared_registry_modified": artifact["declared_registry_modified"],
        "registry_write_requires_explicit_future_phase": artifact[
            "registry_write_requires_explicit_future_phase"
        ],
        "phase_age_false_precision_count": artifact[
            "phase_age_false_precision_count"
        ],
        "current_data_used_to_infer_declared_phase_count": artifact[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "recommended_operator_next_action": artifact[
            "recommended_operator_next_action"
        ],
        "result": artifact["result"],
    }


def _confirmation_options() -> list[dict[str, Any]]:
    return [
        {
            "option_id": "exact_user_declared_start_date",
            "option_label_zh": "使用者提供明確起始日",
            "phase_age_precision": "exact_after_future_registry_update",
            "registry_write_allowed_now": False,
            "data_risk_zh": "最低，但需要使用者明確確認日期與理由。",
        },
        {
            "option_id": "governed_user_declared_start_window",
            "option_label_zh": "使用者確認起始區間",
            "phase_age_precision": "window_only_no_exact_age",
            "registry_write_allowed_now": False,
            "data_risk_zh": "中等，可支援 dashboard 區間顯示，但不可假裝精確天數。",
        },
        {
            "option_id": "keep_unknown_until_more_evidence",
            "option_label_zh": "維持未知，等待更多證據",
            "phase_age_precision": "unknown_or_user_required",
            "registry_write_allowed_now": False,
            "data_risk_zh": "最保守，不提供 phase age 假精度。",
        },
    ]


def _phase_age_false_precision_count(declared_state: Any) -> int:
    if declared_state.declared_phase_start_date is None:
        return int(declared_state.phase_age_status != "unknown_or_user_required")
    return 0


def _passes(artifact: dict[str, Any], spec: dict[str, Any]) -> bool:
    gates = spec["hard_gates"]
    return (
        artifact["declared_current_phase"] == gates["declared_current_phase"]
        and artifact["legal_next_phase"] == gates["legal_next_phase"]
        and artifact["governed_confirmation_option_count"]
        >= gates["governed_confirmation_option_count_minimum"]
        and artifact["registry_write_allowed"] is gates["registry_write_allowed"]
        and artifact["declared_registry_modified"] is gates["declared_registry_modified"]
        and artifact["user_confirmation_required"] is gates["user_confirmation_required"]
        and artifact["phase_age_false_precision_count"]
        == gates["phase_age_false_precision_count"]
        and artifact["current_data_used_to_infer_declared_phase_count"]
        == gates["current_data_used_to_infer_declared_phase_count"]
        and artifact["candidate_phase_emitted"] is gates["candidate_phase_emitted"]
        and artifact["current_phase_emitted"] is gates["current_phase_emitted"]
        and artifact["prohibited_output_field_count"] == 0
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_spec(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "declared_boom_start_governance"
    ]
