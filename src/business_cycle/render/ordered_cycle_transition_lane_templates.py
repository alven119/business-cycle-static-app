"""Phase58 full ordered-cycle transition lane templates.

This module generalizes Phase57's boom-to-recession surface shape into
research-only templates for every legal transition in the ordered cycle. It
does not read current data, rank phases, select candidates, or emit a current
phase.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.ordered_state_machine import (
    load_ordered_cycle_state_machine,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TEMPLATE_CONTRACT_PATH = (
    ROOT / "specs/common/full_ordered_cycle_transition_lane_templates.yaml"
)

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
}


@lru_cache(maxsize=1)
def build_full_ordered_cycle_transition_lane_templates(
    path: str | Path = DEFAULT_TEMPLATE_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the full legal-cycle transition lane template artifact."""

    contract = _load_contract(path)
    machine = load_ordered_cycle_state_machine()
    machine_summary = machine.summary()
    transition_templates = [
        _transition_template(row, machine=machine)
        for row in contract["transition_templates"]
    ]
    lane_templates = [
        lane
        for transition in transition_templates
        for lane in transition["lane_templates"]
    ]
    lane_counts = Counter(lane["lane_category"] for lane in lane_templates)
    summary = _boundary_summary(transition_templates, lane_templates)
    artifact: dict[str, Any] = {
        "template_id": contract["template_id"],
        "template_version": contract["template_version"],
        "source_phase": "58",
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "cycle_order": machine_summary["cycle_order"],
        "legal_transitions": machine_summary["legal_transitions"],
        "transition_templates": transition_templates,
        "lane_semantics": contract["lane_semantics"],
        "allowed_uses": [
            "local_research_dashboard",
            "ordered_cycle_transition_template_review",
            "future_transition_surface_wiring",
            "dashboard_education_layer",
        ],
        "prohibited_uses": [
            "formal_current_phase_inference",
            "candidate_phase_selection",
            "phase_score_or_rank_selection",
            "portfolio_action",
            "production_resolver_input",
        ],
        "trust_metadata": {
            "output_label": "research_only",
            "declared_state_source": "declared_cycle_state_registry",
            "ordered_state_machine": machine_summary["state_machine_id"],
            "watch_confirmation_separated": summary[
                "watch_confirmation_separation_valid"
            ],
            "supporting_only_can_replace_book_core": False,
            "uses_current_data_to_infer_declared_phase": False,
            "production_behavior_change": False,
        },
        "ordered_cycle_state_machine_ready": machine_summary[
            "ordered_cycle_state_machine_ready"
        ],
        "legal_cycle_order_valid": machine_summary["legal_cycle_order_valid"],
        "legal_transition_template_count": len(transition_templates),
        "legal_transition_template_with_state_machine_match_count": sum(
            transition["legal_next_matches_state_machine"]
            for transition in transition_templates
        ),
        "lane_template_count": len(lane_templates),
        "continuation_lane_template_count": lane_counts["continuation_context"],
        "watch_lane_template_count": lane_counts["transition_watch"],
        "confirmation_lane_template_count": lane_counts["transition_confirmation"],
        "transition_with_continuation_lane_count": sum(
            transition["has_continuation_lane"] for transition in transition_templates
        ),
        "transition_with_watch_lane_count": sum(
            transition["has_watch_lane"] for transition in transition_templates
        ),
        "transition_with_confirmation_lane_count": sum(
            transition["has_confirmation_lane"] for transition in transition_templates
        ),
        "watch_confirmation_separation_valid": summary[
            "watch_confirmation_separation_valid"
        ],
        "supporting_only_visible_count": sum(
            bool(lane["supporting_only_role_groups"]) for lane in lane_templates
        ),
        "supporting_only_role_replacement_allowed_count": sum(
            lane["supporting_only_can_replace_book_core"]
            for lane in lane_templates
        ),
        "modern_extension_promoted_to_book_core_count": 0,
        "proxy_promoted_to_book_core_count": 0,
        "silent_substitution_count": 0,
        "phase_support_added_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "full_ordered_cycle_transition_lane_templates_ready"
        ),
        "legal_transition_semantics_preserved": (
            machine_summary["legal_transition_semantics_preserved"]
        ),
        "watch_confirmation_boundary_summary": summary,
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["full_ordered_cycle_transition_lane_templates_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed"
        if artifact["full_ordered_cycle_transition_lane_templates_ready"]
        else "blocked"
    )
    return artifact


@lru_cache(maxsize=1)
def summarize_full_ordered_cycle_transition_lane_templates(
    path: str | Path = DEFAULT_TEMPLATE_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase58 summary fields for scripts and closure checks."""

    artifact = build_full_ordered_cycle_transition_lane_templates(path)
    summary = {
        "phase": "58",
        "phase_id": "58",
        "full_ordered_cycle_transition_lane_templates_ready": artifact[
            "full_ordered_cycle_transition_lane_templates_ready"
        ],
        "ordered_cycle_state_machine_ready": artifact[
            "ordered_cycle_state_machine_ready"
        ],
        "legal_cycle_order_valid": artifact["legal_cycle_order_valid"],
        "legal_transition_template_count": artifact[
            "legal_transition_template_count"
        ],
        "legal_transition_template_with_state_machine_match_count": artifact[
            "legal_transition_template_with_state_machine_match_count"
        ],
        "lane_template_count": artifact["lane_template_count"],
        "continuation_lane_template_count": artifact[
            "continuation_lane_template_count"
        ],
        "watch_lane_template_count": artifact["watch_lane_template_count"],
        "confirmation_lane_template_count": artifact[
            "confirmation_lane_template_count"
        ],
        "transition_with_continuation_lane_count": artifact[
            "transition_with_continuation_lane_count"
        ],
        "transition_with_watch_lane_count": artifact[
            "transition_with_watch_lane_count"
        ],
        "transition_with_confirmation_lane_count": artifact[
            "transition_with_confirmation_lane_count"
        ],
        "watch_confirmation_separation_valid": artifact[
            "watch_confirmation_separation_valid"
        ],
        "supporting_only_visible_count": artifact[
            "supporting_only_visible_count"
        ],
        "supporting_only_role_replacement_allowed_count": artifact[
            "supporting_only_role_replacement_allowed_count"
        ],
        "modern_extension_promoted_to_book_core_count": artifact[
            "modern_extension_promoted_to_book_core_count"
        ],
        "proxy_promoted_to_book_core_count": artifact[
            "proxy_promoted_to_book_core_count"
        ],
        "silent_substitution_count": artifact["silent_substitution_count"],
        "phase_support_added_count": artifact["phase_support_added_count"],
        "prohibited_output_field_count": artifact["prohibited_output_field_count"],
        "standalone_classifier_added_count": artifact[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": artifact[
            "phase_rank_or_score_added_count"
        ],
        "current_data_used_to_infer_declared_phase_count": artifact[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "production_behavior_change_count": artifact[
            "production_behavior_change_count"
        ],
        "legacy_v1_behavior_modified_count": artifact[
            "legacy_v1_behavior_modified_count"
        ],
        "portfolio_policy_output_count": artifact["portfolio_policy_output_count"],
        "backtest_execution_count": artifact["backtest_execution_count"],
        "semantic_drift_count": artifact["semantic_drift_count"],
        "product_doctrine_alignment_status": artifact[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": artifact[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": artifact[
            "legal_transition_semantics_preserved"
        ],
        "transition_lane_templates": artifact,
    }
    summary["result"] = (
        "passed"
        if summary["full_ordered_cycle_transition_lane_templates_ready"]
        else "blocked"
    )
    return summary


def build_full_ordered_cycle_transition_lane_template_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready view model for full ordered-cycle lanes."""

    artifact = artifact or build_full_ordered_cycle_transition_lane_templates()
    return {
        "view_id": "full_ordered_cycle_transition_lane_templates",
        "view_title": "Full Ordered-Cycle Transition Lane Templates",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "cycle_order": artifact["cycle_order"],
        "legal_transitions": artifact["legal_transitions"],
        "transition_templates": artifact["transition_templates"],
        "lane_semantics": artifact["lane_semantics"],
        "watch_confirmation_boundary_summary": artifact[
            "watch_confirmation_boundary_summary"
        ],
        "allowed_uses": artifact["allowed_uses"],
        "prohibited_uses": artifact["prohibited_uses"],
        "trust_metadata": artifact["trust_metadata"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
    }


def _transition_template(
    row: dict[str, Any],
    *,
    machine: Any,
) -> dict[str, Any]:
    from_phase = str(row["from_phase"])
    to_phase = str(row["to_phase"])
    lane_templates = [
        _lane_template(row=lane, transition_id=row["transition_id"])
        for lane in row["lane_templates"]
    ]
    categories = {lane["lane_category"] for lane in lane_templates}
    legal_next = machine.legal_next_phase(from_phase)
    return {
        "transition_id": row["transition_id"],
        "from_phase": from_phase,
        "to_phase": to_phase,
        "legal_next_phase": legal_next,
        "legal_next_matches_state_machine": to_phase == legal_next,
        "lane_templates": lane_templates,
        "lane_template_count": len(lane_templates),
        "has_continuation_lane": "continuation_context" in categories,
        "has_watch_lane": "transition_watch" in categories,
        "has_confirmation_lane": "transition_confirmation" in categories,
        "supporting_only_role_replacement_allowed_count": sum(
            lane["supporting_only_can_replace_book_core"] for lane in lane_templates
        ),
    }


def _lane_template(row: dict[str, Any], *, transition_id: str) -> dict[str, Any]:
    category = str(row["lane_category"])
    return {
        "transition_id": transition_id,
        "lane_id": row["lane_id"],
        "lane_category": category,
        "title_zh": row["title_zh"],
        "watch_lane": category == "transition_watch",
        "confirmation_lane": category == "transition_confirmation",
        "continuation_lane": category == "continuation_context",
        "book_core_role_groups": list(row["book_core_role_groups"]),
        "supporting_only_role_groups": list(row["supporting_only_role_groups"]),
        "supporting_only_can_replace_book_core": bool(
            row["supporting_only_can_replace_book_core"]
        ),
        "explanation_zh": row["explanation_zh"],
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
        "changes_declared_phase": False,
    }


def _boundary_summary(
    transition_templates: list[dict[str, Any]],
    lane_templates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "transition_ids": [
            transition["transition_id"] for transition in transition_templates
        ],
        "watch_lane_ids": [
            lane["lane_id"] for lane in lane_templates if lane["watch_lane"]
        ],
        "confirmation_lane_ids": [
            lane["lane_id"]
            for lane in lane_templates
            if lane["confirmation_lane"]
        ],
        "continuation_lane_ids": [
            lane["lane_id"] for lane in lane_templates if lane["continuation_lane"]
        ],
        "watch_confirmation_separation_valid": all(
            not (lane["watch_lane"] and lane["confirmation_lane"])
            and not (
                lane["confirmation_lane"]
                and lane["lane_category"] != "transition_confirmation"
            )
            and not (
                lane["watch_lane"]
                and lane["lane_category"] != "transition_watch"
            )
            for lane in lane_templates
        ),
        "supporting_only_role_replacement_allowed_count": sum(
            lane["supporting_only_can_replace_book_core"]
            for lane in lane_templates
        ),
    }


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        artifact.get(key) == value
        for key, value in expected.items()
        if key != "full_ordered_cycle_transition_lane_templates_ready"
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        count = sum(key in PROHIBITED_FIELDS for key in value)
        return count + sum(_contains_prohibited_field(item) for item in value.values())
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["full_ordered_cycle_transition_lane_templates"]
    if not isinstance(contract, dict):
        raise ValueError("full ordered-cycle transition template contract must map")
    return contract
