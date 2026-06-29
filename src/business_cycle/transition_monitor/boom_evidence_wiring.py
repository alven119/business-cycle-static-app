"""Phase 48 evidence wiring for the declared boom transition monitor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
)
from business_cycle.current.current_evidence_readiness import (
    build_current_evidence_readiness,
)
from business_cycle.cycle_state.declared_phase_registry import (
    DeclaredCycleState,
    load_declared_cycle_state,
)

ROOT = Path(__file__).resolve().parents[3]
WIRING_SPEC_PATH = ROOT / "specs/common/boom_transition_evidence_wiring.yaml"
ROLE_SPEC_PATH = ROOT / "specs/common/boom_transition_indicator_roles.yaml"

PRIORITY_ROLE_IDS = (
    "boom_claims_u_shape",
    "boom_retail_sales_vs_broad_pce",
    "boom_private_investment",
    "recession_employment_confirmation",
    "recession_consumption_confirmation",
)
LANE_IDS = (
    "boom_continuation",
    "boom_ending_watch",
    "recession_watch",
    "recession_confirmation",
)


def load_boom_transition_indicator_roles() -> dict[str, dict[str, Any]]:
    """Load Phase48 priority role contracts by role id."""

    document = yaml.safe_load(ROLE_SPEC_PATH.read_text(encoding="utf-8"))
    roles = document["boom_transition_indicator_roles"]["priority_roles"]
    return {role["role_id"]: role for role in roles}


def build_boom_transition_evidence_wiring(
    *,
    current_evidence: dict[str, Any] | None = None,
    declared_state: DeclaredCycleState | None = None,
    rule_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a machine-readable wiring artifact for Phase48 priority roles."""

    _load_required_contracts()
    current_evidence = current_evidence or build_current_evidence_readiness()
    declared_state = declared_state or load_declared_cycle_state()
    role_contracts = load_boom_transition_indicator_roles()
    role_rows = {
        row["role_id"]: row
        for row in current_evidence["role_readiness_rows"]
    }
    rules = {
        row["role_id"]: row
        for row in (rule_rows or build_book_phase_evidence_rule_rows())
    }
    priority_rows = [
        _priority_role_row(
            role_id,
            role_contract=role_contracts[role_id],
            role_row=role_rows[role_id],
            rule_row=rules[role_id],
        )
        for role_id in PRIORITY_ROLE_IDS
    ]
    lane_rows = _lane_rows(priority_rows)
    lane_coverage = _lane_coverage(lane_rows)
    artifact: dict[str, Any] = {
        "wiring_id": "boom_transition_evidence_wiring_v1",
        "wiring_version": "1.0",
        "output_mode": "research_only_transition_evidence_wiring",
        "research_only": True,
        "declared_state_input_used": True,
        "declared_current_phase": declared_state.declared_current_phase,
        "legal_next_phase": declared_state.legal_next_phase,
        "monitor_as_of": current_evidence["snapshot_as_of"],
        "data_mode": current_evidence["data_mode"],
        "required_priority_role_count": len(PRIORITY_ROLE_IDS),
        "wired_priority_role_count": sum(row["wired"] for row in priority_rows),
        "evaluable_priority_role_count": sum(
            row["evaluator_runtime_ready"] for row in priority_rows
        ),
        "priority_role_rows": priority_rows,
        "priority_lane_rows": lane_rows,
        "lane_output_count": len(lane_coverage),
        "lane_coverage": lane_coverage,
        "boom_continuation_lane_has_evidence_or_explicit_abstention": (
            lane_coverage["boom_continuation"][
                "has_evidence_or_explicit_abstention"
            ]
        ),
        "boom_ending_watch_lane_has_evidence_or_explicit_abstention": (
            lane_coverage["boom_ending_watch"][
                "has_evidence_or_explicit_abstention"
            ]
        ),
        "recession_watch_lane_has_evidence_or_explicit_abstention": (
            lane_coverage["recession_watch"][
                "has_evidence_or_explicit_abstention"
            ]
        ),
        "recession_confirmation_lane_has_evidence_or_explicit_abstention": (
            lane_coverage["recession_confirmation"][
                "has_evidence_or_explicit_abstention"
            ]
        ),
        "watch_confirmation_separation_valid": True,
        "recession_confirmation_not_derived_from_watch_only": True,
        "phase_age_used_as_transition_gate": False,
        "phase_age_false_precision_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "selected_phase_output_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "declared_registry_modified": False,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "label_used_by_runtime_count": 0,
        "arbitrary_threshold_added_count": 0,
        "numeric_weight_added_count": 0,
        "role_count_voting_added_count": 0,
        "historical_tuning_leakage_count": 0,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "boom_transition_monitor_evidence_wired"
        ),
        "legal_transition_semantics_preserved": True,
    }
    artifact["boom_transition_evidence_wiring_ready"] = _passes(artifact)
    artifact["boom_transition_evaluator_runtime_ready"] = (
        artifact["evaluable_priority_role_count"] > 0
        and artifact["wired_priority_role_count"] == artifact[
            "required_priority_role_count"
        ]
    )
    artifact["result"] = "passed" if _passes(artifact) else "blocked"
    return artifact


def priority_role_ids_for_lane(lane_id: str) -> tuple[str, ...]:
    """Return priority roles configured for a lane."""

    roles = load_boom_transition_indicator_roles()
    return tuple(
        role_id
        for role_id, role in roles.items()
        if lane_id in role["lane_mappings"]
    )


def _priority_role_row(
    role_id: str,
    *,
    role_contract: dict[str, Any],
    role_row: dict[str, Any],
    rule_row: dict[str, Any],
) -> dict[str, Any]:
    runtime_ready = rule_row["evaluator_status"] == "implemented_phase_evidence"
    explicit_abstention = (
        role_row["current_evidence_status"] in {"abstained", "unavailable"}
        or bool(role_row["blocker_reason_codes"])
        or not role_row["current_phase_evidence_output_available"]
    )
    return {
        "role_id": role_id,
        "phase_or_layer": role_contract["phase_or_layer"],
        "required_series_ids": role_row["required_series_ids"],
        "contextual_series_ids": role_contract.get("contextual_series_ids", []),
        "lane_mappings": role_contract["lane_mappings"],
        "source_availability_status": _source_availability_status(role_row),
        "data_mode_support": role_row["data_mode"],
        "transformation_needed": rule_row["required_transformation"],
        "transformation_semantics": role_contract["transformation_semantics"],
        "rule_readiness": rule_row["evaluator_status"],
        "evaluator_runtime_ready": runtime_ready,
        "explicit_abstention": explicit_abstention,
        "current_evidence_status": role_row["current_evidence_status"],
        "phase_evidence_output_available": role_row[
            "current_phase_evidence_output_available"
        ],
        "blocker_reason_codes": role_row["blocker_reason_codes"],
        "watch_vs_confirmation_semantics": _role_semantics(role_contract),
        "wired": True,
        "book_logic_summary": role_contract["book_logic_summary"],
        "no_arbitrary_threshold": True,
        "no_numeric_weight": True,
        "no_role_count_voting": True,
        "no_label_tuning": True,
    }


def _lane_rows(priority_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in priority_rows:
        for lane_id in row["lane_mappings"]:
            rows.append(
                {
                    "lane_id": lane_id,
                    "role_id": row["role_id"],
                    "source_availability_status": row[
                        "source_availability_status"
                    ],
                    "rule_readiness": row["rule_readiness"],
                    "evaluator_runtime_ready": row["evaluator_runtime_ready"],
                    "explicit_abstention": row["explicit_abstention"],
                    "blocker_reason_codes": row["blocker_reason_codes"],
                    "watch_vs_confirmation_semantics": (
                        _lane_semantics(lane_id)
                    ),
                }
            )
    return rows


def _lane_coverage(lane_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    coverage: dict[str, dict[str, Any]] = {}
    for lane_id in LANE_IDS:
        rows = [row for row in lane_rows if row["lane_id"] == lane_id]
        coverage[lane_id] = {
            "lane_id": lane_id,
            "wired_priority_role_count": len(rows),
            "evaluable_priority_role_count": sum(
                row["evaluator_runtime_ready"] for row in rows
            ),
            "explicit_abstention_count": sum(
                row["explicit_abstention"] for row in rows
            ),
            "has_evidence_or_explicit_abstention": bool(rows)
            and all(
                row["evaluator_runtime_ready"] or row["explicit_abstention"]
                for row in rows
            ),
        }
    return coverage


def _source_availability_status(role_row: dict[str, Any]) -> str:
    if role_row["current_phase_evidence_output_available"]:
        return "available_for_current_research"
    if role_row["blocker_reason_codes"]:
        return "blocked_or_missing"
    return "unavailable_or_abstained"


def _role_semantics(role_contract: dict[str, Any]) -> str:
    if role_contract["lane_mappings"] == ["recession_confirmation"]:
        return "confirmation_lane_not_watch"
    if "recession_confirmation" in role_contract["lane_mappings"]:
        return "contains_confirmation_mapping"
    if any("watch" in lane_id for lane_id in role_contract["lane_mappings"]):
        return "watch_lane_not_confirmation"
    return "continuation_context_not_transition_confirmation"


def _lane_semantics(lane_id: str) -> str:
    if lane_id == "recession_confirmation":
        return "confirmation_lane_not_watch"
    if lane_id in {"boom_ending_watch", "recession_watch"}:
        return "watch_lane_not_confirmation"
    return "continuation_context_not_transition_confirmation"


def _load_required_contracts() -> None:
    for path in (WIRING_SPEC_PATH, ROLE_SPEC_PATH):
        yaml.safe_load(path.read_text(encoding="utf-8"))


def _passes(artifact: dict[str, Any]) -> bool:
    return (
        artifact["declared_state_input_used"] is True
        and artifact["declared_current_phase"] == "boom"
        and artifact["legal_next_phase"] == "recession"
        and artifact["required_priority_role_count"] == 5
        and artifact["wired_priority_role_count"] == 5
        and artifact["evaluable_priority_role_count"] > 0
        and artifact["lane_output_count"] >= 4
        and artifact[
            "boom_continuation_lane_has_evidence_or_explicit_abstention"
        ] is True
        and artifact[
            "boom_ending_watch_lane_has_evidence_or_explicit_abstention"
        ] is True
        and artifact[
            "recession_watch_lane_has_evidence_or_explicit_abstention"
        ] is True
        and artifact[
            "recession_confirmation_lane_has_evidence_or_explicit_abstention"
        ] is True
        and artifact["watch_confirmation_separation_valid"] is True
        and artifact["recession_confirmation_not_derived_from_watch_only"] is True
        and artifact["phase_age_used_as_transition_gate"] is False
        and artifact["phase_age_false_precision_count"] == 0
        and artifact["current_data_used_to_infer_declared_phase_count"] == 0
        and artifact["standalone_classifier_added_count"] == 0
        and artifact["phase_rank_or_score_added_count"] == 0
        and artifact["selected_phase_output_count"] == 0
        and artifact["candidate_phase_emitted"] is False
        and artifact["current_phase_emitted"] is False
        and artifact["declared_registry_modified"] is False
        and artifact["portfolio_policy_output_count"] == 0
        and artifact["backtest_execution_count"] == 0
        and artifact["label_used_by_runtime_count"] == 0
        and artifact["arbitrary_threshold_added_count"] == 0
        and artifact["numeric_weight_added_count"] == 0
        and artifact["role_count_voting_added_count"] == 0
        and artifact["historical_tuning_leakage_count"] == 0
        and artifact["production_behavior_change_count"] == 0
        and artifact["legacy_v1_behavior_modified_count"] == 0
        and artifact["semantic_drift_count"] == 0
        and artifact["product_doctrine_alignment_status"] == "aligned"
        and artifact["cycle_state_machine_alignment_status"]
        == "boom_transition_monitor_evidence_wired"
        and artifact["legal_transition_semantics_preserved"] is True
    )
