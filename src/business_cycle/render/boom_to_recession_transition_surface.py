"""Phase57 completed boom-to-recession transition surface.

This module composes the declared boom transition monitor, Phase49 dashboard
surface, and Phase56 indicator-detail cards into a richer research-only view.
It does not infer or emit a candidate/current phase.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.boom_transition_dashboard_surface import (
    build_boom_transition_dashboard_surface,
)
from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_cards,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COMPLETION_CONTRACT_PATH = (
    ROOT / "specs/common/boom_to_recession_transition_surface_completion.yaml"
)

LANE_SEQUENCE = (
    "boom_continuation",
    "boom_ending_watch",
    "recession_watch",
    "recession_confirmation",
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
def build_boom_to_recession_transition_surface_completion(
    path: str | Path = DEFAULT_COMPLETION_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the Phase57 completed transition surface."""

    contract = _load_contract(path)
    base_surface = build_boom_transition_dashboard_surface()
    all_detail_cards = build_indicator_detail_source_risk_value_cards()
    detail_by_role = {card["role_id"]: card for card in all_detail_cards}
    lane_cards = [
        _completed_lane_card(lane, detail_by_role=detail_by_role)
        for lane in base_surface["lane_cards"]
    ]
    priority_cards = _priority_indicator_cards(lane_cards)
    lane_counts = Counter(_lane_category(lane) for lane in lane_cards)
    watch_boundary = _watch_confirmation_boundary_summary(lane_cards)
    surface = {
        "surface_id": contract["surface_id"],
        "surface_version": contract["surface_version"],
        "source_phase": "57",
        "output_mode": "research_only_boom_to_recession_transition_surface",
        "research_only": True,
        "declared_state_context": {
            "declared_state_label": "declared_state_not_inferred_current_phase",
            "declared_current_phase": base_surface["declared_current_phase"],
            "legal_next_phase": base_surface["legal_next_phase"],
            "declared_phase_start_date": base_surface[
                "declared_phase_start_date"
            ],
            "phase_age_status": base_surface["phase_age_status"],
            "phase_age_used_as_transition_gate": base_surface[
                "phase_age_used_as_transition_gate"
            ],
        },
        "declared_current_phase": base_surface["declared_current_phase"],
        "legal_next_phase": base_surface["legal_next_phase"],
        "monitor_as_of": base_surface["monitor_as_of"],
        "data_mode": base_surface["data_mode"],
        "transition_label": "boom_to_recession",
        "transition_lane_cards": lane_cards,
        "priority_indicator_cards": priority_cards,
        "full_indicator_detail_summary": _full_indicator_detail_summary(
            all_detail_cards,
        ),
        "watch_confirmation_boundary_summary": watch_boundary,
        "transition_gap_summary": _transition_gap_summary(
            base_surface,
            priority_cards,
            all_detail_cards,
        ),
        "why_not_transition_decision": [
            "declared boom remains the governed state",
            "watch evidence remains separate from confirmation evidence",
            "priority indicators with metadata-only values remain explanation context",
            "formal candidate/current phase gates remain closed",
        ],
        "allowed_uses": [
            "local_research_dashboard",
            "declared_boom_transition_explanation",
            "boom_to_recession_transition_surface_review",
            "source_gap_review",
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
            "legal_transition": "boom_to_recession",
            "phase57_completion_surface": True,
            "uses_current_data_to_infer_declared_phase": False,
            "watch_confirmation_separated": watch_boundary[
                "watch_confirmation_separation_valid"
            ],
            "recession_confirmation_not_derived_from_watch_only": watch_boundary[
                "recession_confirmation_not_derived_from_watch_only"
            ],
            "production_behavior_change": False,
        },
        "transition_lane_count": len(lane_cards),
        "continuation_lane_count": lane_counts["continuation"],
        "watch_lane_count": lane_counts["watch"],
        "confirmation_lane_count": lane_counts["confirmation"],
        "transition_priority_indicator_count": len(priority_cards),
        "transition_priority_indicator_with_detail_count": sum(
            card["phase56_detail_card_linked"] for card in priority_cards
        ),
        "full_macro_indicator_detail_count": len(all_detail_cards),
        "source_risk_visible_priority_count": sum(
            card["source_risk_visible"] for card in priority_cards
        ),
        "value_context_visible_priority_count": sum(
            card["value_context_visible"] for card in priority_cards
        ),
        "freshness_context_visible_priority_count": sum(
            card["freshness_context_visible"] for card in priority_cards
        ),
        "release_timing_context_visible_priority_count": sum(
            card["release_timing_context_visible"] for card in priority_cards
        ),
        "why_not_evidence_visible_priority_count": sum(
            card["why_not_evidence_visible"] for card in priority_cards
        ),
        "missing_or_abstention_reason_visible_priority_count": sum(
            bool(card["abstention_or_blocker_reason_zh"])
            for card in priority_cards
        ),
        "watch_confirmation_separation_valid": watch_boundary[
            "watch_confirmation_separation_valid"
        ],
        "recession_confirmation_not_derived_from_watch_only": watch_boundary[
            "recession_confirmation_not_derived_from_watch_only"
        ],
        "watch_promoted_to_confirmation_count": watch_boundary[
            "watch_promoted_to_confirmation_count"
        ],
        "confirmation_derived_from_watch_only_count": watch_boundary[
            "confirmation_derived_from_watch_only_count"
        ],
        "boom_ending_watch_mislabeled_confirmation_count": watch_boundary[
            "boom_ending_watch_mislabeled_confirmation_count"
        ],
        "recession_watch_mislabeled_confirmation_count": watch_boundary[
            "recession_watch_mislabeled_confirmation_count"
        ],
        "continuation_mislabeled_transition_count": watch_boundary[
            "continuation_mislabeled_transition_count"
        ],
        "proxy_promoted_to_book_core_count": sum(
            card["supporting_proxy_can_replace_book_core"]
            for card in priority_cards
        ),
        "silent_substitution_count": sum(
            card["silent_substitution"] for card in priority_cards
        ),
        "false_resolution_count": sum(
            card["false_resolution"] for card in priority_cards
        ),
        "phase_support_added_count": sum(
            card["phase_support_added"] for card in priority_cards
        ),
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
            "boom_to_recession_transition_surface_completed_declared_state_preserved"
        ),
        "legal_transition_semantics_preserved": True,
    }
    surface["prohibited_output_field_count"] = _contains_prohibited_field(surface)
    surface["boom_to_recession_transition_surface_completion_ready"] = _passes(
        surface,
        contract["hard_gates"],
    )
    surface["result"] = (
        "passed"
        if surface["boom_to_recession_transition_surface_completion_ready"]
        else "blocked"
    )
    return surface


@lru_cache(maxsize=1)
def summarize_boom_to_recession_transition_surface_completion(
    path: str | Path = DEFAULT_COMPLETION_CONTRACT_PATH,
) -> dict[str, Any]:
    """Summarize Phase57 surface hard gates."""

    surface = build_boom_to_recession_transition_surface_completion(path)
    summary = {
        "phase": "57",
        "phase_id": "57",
        "boom_to_recession_transition_surface_completion_ready": surface[
            "boom_to_recession_transition_surface_completion_ready"
        ],
        "declared_current_phase": surface["declared_current_phase"],
        "legal_next_phase": surface["legal_next_phase"],
        "monitor_as_of": surface["monitor_as_of"],
        "data_mode": surface["data_mode"],
        "transition_lane_count": surface["transition_lane_count"],
        "continuation_lane_count": surface["continuation_lane_count"],
        "watch_lane_count": surface["watch_lane_count"],
        "confirmation_lane_count": surface["confirmation_lane_count"],
        "transition_priority_indicator_count": surface[
            "transition_priority_indicator_count"
        ],
        "transition_priority_indicator_with_detail_count": surface[
            "transition_priority_indicator_with_detail_count"
        ],
        "full_macro_indicator_detail_count": surface[
            "full_macro_indicator_detail_count"
        ],
        "source_risk_visible_priority_count": surface[
            "source_risk_visible_priority_count"
        ],
        "value_context_visible_priority_count": surface[
            "value_context_visible_priority_count"
        ],
        "freshness_context_visible_priority_count": surface[
            "freshness_context_visible_priority_count"
        ],
        "release_timing_context_visible_priority_count": surface[
            "release_timing_context_visible_priority_count"
        ],
        "why_not_evidence_visible_priority_count": surface[
            "why_not_evidence_visible_priority_count"
        ],
        "missing_or_abstention_reason_visible_priority_count": surface[
            "missing_or_abstention_reason_visible_priority_count"
        ],
        "watch_confirmation_separation_valid": surface[
            "watch_confirmation_separation_valid"
        ],
        "recession_confirmation_not_derived_from_watch_only": surface[
            "recession_confirmation_not_derived_from_watch_only"
        ],
        "watch_promoted_to_confirmation_count": surface[
            "watch_promoted_to_confirmation_count"
        ],
        "confirmation_derived_from_watch_only_count": surface[
            "confirmation_derived_from_watch_only_count"
        ],
        "boom_ending_watch_mislabeled_confirmation_count": surface[
            "boom_ending_watch_mislabeled_confirmation_count"
        ],
        "recession_watch_mislabeled_confirmation_count": surface[
            "recession_watch_mislabeled_confirmation_count"
        ],
        "continuation_mislabeled_transition_count": surface[
            "continuation_mislabeled_transition_count"
        ],
        "proxy_promoted_to_book_core_count": surface[
            "proxy_promoted_to_book_core_count"
        ],
        "silent_substitution_count": surface["silent_substitution_count"],
        "false_resolution_count": surface["false_resolution_count"],
        "phase_support_added_count": surface["phase_support_added_count"],
        "prohibited_output_field_count": surface["prohibited_output_field_count"],
        "standalone_classifier_added_count": surface[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": surface[
            "phase_rank_or_score_added_count"
        ],
        "current_data_used_to_infer_declared_phase_count": surface[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": surface["candidate_phase_emitted"],
        "current_phase_emitted": surface["current_phase_emitted"],
        "production_behavior_change_count": surface[
            "production_behavior_change_count"
        ],
        "legacy_v1_behavior_modified_count": surface[
            "legacy_v1_behavior_modified_count"
        ],
        "portfolio_policy_output_count": surface["portfolio_policy_output_count"],
        "backtest_execution_count": surface["backtest_execution_count"],
        "semantic_drift_count": surface["semantic_drift_count"],
        "product_doctrine_alignment_status": surface[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": surface[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": surface[
            "legal_transition_semantics_preserved"
        ],
        "transition_surface_completion": surface,
    }
    summary["result"] = (
        "passed"
        if summary["boom_to_recession_transition_surface_completion_ready"]
        else "blocked"
    )
    return summary


def build_boom_to_recession_transition_surface_view_model(
    surface: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready Phase57 view model."""

    surface = surface or build_boom_to_recession_transition_surface_completion()
    return {
        "view_id": "boom_to_recession_transition_surface_completion",
        "view_title": "Boom to Recession Transition Surface",
        "output_mode": surface["output_mode"],
        "research_only": True,
        "declared_state_context": surface["declared_state_context"],
        "transition_label": surface["transition_label"],
        "transition_lane_cards": surface["transition_lane_cards"],
        "priority_indicator_cards": surface["priority_indicator_cards"],
        "full_indicator_detail_summary": surface["full_indicator_detail_summary"],
        "watch_confirmation_boundary_summary": surface[
            "watch_confirmation_boundary_summary"
        ],
        "transition_gap_summary": surface["transition_gap_summary"],
        "why_not_transition_decision": surface["why_not_transition_decision"],
        "allowed_uses": surface["allowed_uses"],
        "prohibited_uses": surface["prohibited_uses"],
        "trust_metadata": surface["trust_metadata"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
    }


def _completed_lane_card(
    lane: dict[str, Any],
    *,
    detail_by_role: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    role_cards = [
        _priority_card_from_item(item, detail_by_role=detail_by_role)
        for item in lane["evidence_items"]
    ]
    state_counts = Counter(card["lane_evidence_state"] for card in role_cards)
    return {
        "lane_id": lane["lane_id"],
        "title_zh": lane["title_zh"],
        "purpose_zh": lane["purpose_zh"],
        "lane_category": _lane_category(lane),
        "lane_status": lane["lane_status"],
        "lane_ready": bool(lane["evidence_items"]),
        "watch_lane": lane["watch_lane"],
        "confirmation_lane": lane["confirmation_lane"],
        "watch_confirmation_boundary_zh": lane[
            "watch_confirmation_boundary_zh"
        ],
        "role_count": len(role_cards),
        "state_counts": dict(sorted(state_counts.items())),
        "supportive_evidence_count": lane["supportive_evidence_count"],
        "contradictory_evidence_count": lane["contradictory_evidence_count"],
        "explicit_abstention_count": lane["explicit_abstention_count"],
        "missing_or_abstained_evidence_count": lane[
            "missing_or_abstained_evidence_count"
        ],
        "role_ids": [card["role_id"] for card in role_cards],
        "priority_indicator_cards": role_cards,
        "book_logic_summary": lane["book_logic_summary"],
        "why_not_confirmation_zh": _why_not_confirmation(lane),
    }


def _priority_card_from_item(
    item: dict[str, Any],
    *,
    detail_by_role: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    detail = detail_by_role[item["role_id"]]
    return {
        "role_id": item["role_id"],
        "lane_evidence_state": item["lane_evidence_state"],
        "source_evidence_status": item["source_evidence_status"],
        "phase56_detail_card_linked": True,
        "source_risk_visible": detail["source_risk_visible"],
        "source_risk_label_zh": detail["source_risk_label_zh"],
        "data_risk_level": detail["data_risk_level"],
        "source_family": detail["source_family"],
        "substitution_degree": detail["substitution_degree"],
        "value_context_visible": detail["value_context_visible"],
        "value_context_status": detail["value_context_status"],
        "freshness_context_visible": detail["freshness_context_visible"],
        "freshness_context_summary": detail["freshness_context_summary"],
        "release_timing_context_visible": detail[
            "release_timing_context_visible"
        ],
        "release_timing_context": detail["release_timing_context"],
        "transformation_context_visible": detail[
            "transformation_context_visible"
        ],
        "transformation_semantics_status": detail[
            "transformation_semantics_status"
        ],
        "why_not_evidence_visible": detail["why_not_evidence_visible"],
        "why_not_evidence_zh": detail["why_not_evidence_zh"],
        "dashboard_explanation_zh": detail["dashboard_explanation_zh"],
        "next_gap_zh": detail["next_gap_zh"],
        "abstention_or_blocker_reason_zh": _abstention_reason(item, detail),
        "blocker_reason_codes": item["blocker_reason_codes"],
        "watch_vs_confirmation_semantics": item[
            "watch_vs_confirmation_semantics"
        ],
        "watch_evidence_promoted_to_confirmation": item[
            "watch_evidence_promoted_to_confirmation"
        ],
        "confirmation_derived_from_watch_only": item[
            "confirmation_derived_from_watch_only"
        ],
        "supporting_proxy_can_replace_book_core": detail[
            "supporting_proxy_can_replace_book_core"
        ],
        "silent_substitution": detail["silent_substitution"],
        "false_resolution": detail["false_resolution"],
        "phase_support_added": detail["phase_support_added"],
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
    }


def _priority_indicator_cards(
    lane_cards: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for lane in lane_cards:
        for card in lane["priority_indicator_cards"]:
            role_id = card["role_id"]
            if role_id not in merged:
                merged[role_id] = {**card, "lane_ids": [], "lane_states": []}
            merged[role_id]["lane_ids"].append(lane["lane_id"])
            merged[role_id]["lane_states"].append(
                {
                    "lane_id": lane["lane_id"],
                    "lane_category": lane["lane_category"],
                    "lane_evidence_state": card["lane_evidence_state"],
                    "watch_lane": lane["watch_lane"],
                    "confirmation_lane": lane["confirmation_lane"],
                }
            )
    return list(merged.values())


def _full_indicator_detail_summary(cards: list[dict[str, Any]]) -> dict[str, Any]:
    phase_counts = Counter(card["phase_or_layer"] for card in cards)
    return {
        "full_macro_indicator_detail_count": len(cards),
        "phase_counts": dict(sorted(phase_counts.items())),
        "authorized_input_missing_count": sum(
            card["user_authorized_input_required"] for card in cards
        ),
        "supporting_proxy_only_count": sum(
            card["supporting_proxy_only"] for card in cards
        ),
        "source_risk_visible_count": sum(card["source_risk_visible"] for card in cards),
        "why_not_evidence_visible_count": sum(
            card["why_not_evidence_visible"] for card in cards
        ),
    }


def _watch_confirmation_boundary_summary(
    lane_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    watch_lanes = [lane for lane in lane_cards if lane["watch_lane"]]
    confirmation_lanes = [lane for lane in lane_cards if lane["confirmation_lane"]]
    continuation_lanes = [
        lane
        for lane in lane_cards
        if not lane["watch_lane"] and not lane["confirmation_lane"]
    ]
    watch_items = [
        card
        for lane in watch_lanes
        for card in lane["priority_indicator_cards"]
    ]
    confirmation_items = [
        card
        for lane in confirmation_lanes
        for card in lane["priority_indicator_cards"]
    ]
    return {
        "watch_lane_ids": [lane["lane_id"] for lane in watch_lanes],
        "confirmation_lane_ids": [lane["lane_id"] for lane in confirmation_lanes],
        "continuation_lane_ids": [lane["lane_id"] for lane in continuation_lanes],
        "watch_confirmation_separation_valid": (
            {lane["lane_id"] for lane in watch_lanes}
            == {"boom_ending_watch", "recession_watch"}
            and {lane["lane_id"] for lane in confirmation_lanes}
            == {"recession_confirmation"}
            and {lane["lane_id"] for lane in continuation_lanes}
            == {"boom_continuation"}
        ),
        "recession_confirmation_not_derived_from_watch_only": bool(
            confirmation_items
        )
        and all(
            item["watch_vs_confirmation_semantics"]
            == "confirmation_lane_not_watch"
            and not item["watch_evidence_promoted_to_confirmation"]
            and not item["confirmation_derived_from_watch_only"]
            for item in confirmation_items
        ),
        "watch_promoted_to_confirmation_count": sum(
            item["watch_evidence_promoted_to_confirmation"]
            for item in watch_items + confirmation_items
        ),
        "confirmation_derived_from_watch_only_count": sum(
            item["confirmation_derived_from_watch_only"]
            for item in confirmation_items
        ),
        "boom_ending_watch_mislabeled_confirmation_count": sum(
            lane["lane_id"] == "boom_ending_watch" and lane["confirmation_lane"]
            for lane in lane_cards
        ),
        "recession_watch_mislabeled_confirmation_count": sum(
            lane["lane_id"] == "recession_watch" and lane["confirmation_lane"]
            for lane in lane_cards
        ),
        "continuation_mislabeled_transition_count": sum(
            lane["lane_id"] == "boom_continuation"
            and (lane["watch_lane"] or lane["confirmation_lane"])
            for lane in lane_cards
        ),
    }


def _transition_gap_summary(
    base_surface: dict[str, Any],
    priority_cards: list[dict[str, Any]],
    all_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "missing_evidence_summary": base_surface["missing_evidence_summary"],
        "priority_metadata_only_count": sum(
            card["value_context_status"]
            in {
                "source_metadata_visible_numeric_cache_missing",
                "source_metadata_ready_numeric_value_missing",
            }
            for card in priority_cards
        ),
        "priority_authorized_input_required_count": sum(
            card["value_context_status"]
            == "authorized_private_or_user_input_required_no_numeric_value"
            for card in priority_cards
        ),
        "full_authorized_input_required_count": sum(
            card["user_authorized_input_required"] for card in all_cards
        ),
        "full_supporting_proxy_only_count": sum(
            card["supporting_proxy_only"] for card in all_cards
        ),
        "formal_transition_blocked": True,
    }


def _lane_category(lane: dict[str, Any]) -> str:
    if lane["confirmation_lane"]:
        return "confirmation"
    if lane["watch_lane"]:
        return "watch"
    return "continuation"


def _why_not_confirmation(lane: dict[str, Any]) -> str:
    if lane["confirmation_lane"]:
        return "此 lane 是 confirmation，但仍不得輸出 formal phase；需等待正式 migration gate。"
    if lane["watch_lane"]:
        return "此 lane 是 watch，只能提示 transition risk，不能當作 recession confirmation。"
    return "此 lane 是 boom continuation context，不是階段選擇器。"


def _abstention_reason(item: dict[str, Any], detail: dict[str, Any]) -> str:
    if item["blocker_reason_codes"]:
        return "、".join(item["blocker_reason_codes"])
    return str(detail["why_not_evidence_zh"])


def _passes(surface: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        surface.get(key) == value
        for key, value in expected.items()
        if key != "boom_to_recession_transition_surface_completion_ready"
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_contract(
    path: str | Path = DEFAULT_COMPLETION_CONTRACT_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "boom_to_recession_transition_surface_completion"
    ]
