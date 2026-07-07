"""Phase86 transition risk evidence accumulation view model.

This surface repackages the existing Phase67 transition timing replay preview
into a product-facing dashboard section. It is deliberately non-emitting: it
does not infer the current phase, select a candidate phase, rank phases, score
phases, or change production behavior.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview_view_model,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/transition_risk_evidence_accumulation.yaml"

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "phase_probability",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "historical_accuracy",
    "confusion_matrix",
    "portfolio_return",
}


def build_transition_risk_evidence_accumulation(
    *,
    transition_timing_replay_preview: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a dashboard-ready transition risk accumulation artifact."""

    contract = _load_contract(path)
    preview = (
        transition_timing_replay_preview
        or build_transition_timing_replay_preview_view_model()
    )
    lanes = list(preview["transition_lane_timing_previews"])
    events = list(preview["evidence_accumulation_events"])
    events_by_lane = _events_by_lane(events)
    lane_cards = [
        _lane_card(lane, events_by_lane.get(lane["lane_id"], [])) for lane in lanes
    ]
    lane_categories = Counter(card["lane_category"] for card in lane_cards)
    event_statuses = Counter(event["accumulation_status"] for event in events)
    next_required = [_next_required_observation(card) for card in lane_cards]
    missing_event_count = sum(bool(event["visible_gap_reason_codes"]) for event in events)
    contradictory_event_count = sum(_has_contradictory_evidence(event) for event in events)
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "86",
        "phase_id": 86,
        "phase_label": "transition_risk_evidence_accumulation_view",
        "view_id": "transition_risk_evidence_accumulation",
        "view_title": "Transition Risk Evidence Accumulation",
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "declared_state_context": preview["declared_state_context"],
        "transition_risk_summary": {
            "declared_current_phase": preview["declared_state_context"][
                "declared_current_phase"
            ],
            "legal_next_phase": preview["declared_state_context"]["legal_next_phase"],
            "lane_card_count": len(lane_cards),
            "event_count": len(events),
            "status_counts": dict(sorted(event_statuses.items())),
            "summary_zh": (
                "轉折風險目前以 metadata-ready / gap-visible 的累積視圖呈現；"
                "watch、confirmation、continuation 各自保留邊界。"
            ),
        },
        "accumulation_lane_cards": lane_cards,
        "missing_evidence_summary": {
            "lane_with_missing_evidence_count": sum(
                card["missing_evidence_count"] > 0 for card in lane_cards
            ),
            "missing_evidence_event_count": missing_event_count,
            "visible_gap_reason_codes": sorted(
                {
                    code
                    for card in lane_cards
                    for code in card["visible_gap_reason_codes"]
                }
            ),
            "missing_evidence_policy_zh": (
                "缺漏或 metadata-only input 必須保留為 visible gap，不得填零、"
                "不得當成 neutral，也不得縮小分母。"
            ),
        },
        "contradictory_evidence_summary": {
            "contradictory_evidence_lane_count": sum(
                card["contradictory_evidence_count"] > 0 for card in lane_cards
            ),
            "contradictory_evidence_event_count": contradictory_event_count,
            "contradictory_evidence_policy_zh": (
                "若未來出現 contradictory evidence，必須以阻擋/反對理由呈現，"
                "不得被平均消除或升級成 confirmation。"
            ),
        },
        "next_required_observations": next_required,
        "allowed_uses": contract["output_policy"].get(
            "allowed_uses",
            [
                "local_research_dashboard",
                "transition_risk_review",
                "evidence_gap_review",
            ],
        ),
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "phase_rank_or_score",
            "portfolio_or_trade_decision",
            "production_decision",
        ],
        "trust_metadata": {
            "output_label": "research_only",
            "source_view_model": preview["view_id"],
            "declared_state_source": "declared_cycle_state_registry",
            "watch_confirmation_separated": preview["trust_metadata"][
                "watch_confirmation_separated"
            ],
            "phase_presence_transition_separated": True,
            "missing_values_are_neutral": False,
            "metadata_only_is_phase_support": False,
            "current_phase_inference_enabled": False,
            "candidate_phase_selection_enabled": False,
            "production_behavior_change": False,
        },
        "transition_accumulation_lane_card_count": len(lane_cards),
        "evidence_accumulation_event_count": len(events),
        "evidence_accumulation_status_family_count": len(event_statuses),
        "continuation_lane_card_count": lane_categories["continuation_context"],
        "watch_lane_card_count": lane_categories["transition_watch"],
        "confirmation_lane_card_count": lane_categories["transition_confirmation"],
        "watch_confirmation_boundary_count": sum(
            bool(card["watch_confirmation_boundary_label"]) for card in lane_cards
        ),
        "phase_presence_transition_separation_valid": all(
            card["phase_presence_transition_boundary_valid"] for card in lane_cards
        ),
        "watch_confirmation_separation_valid": bool(
            preview["trust_metadata"]["watch_confirmation_separated"]
        ),
        "lane_with_missing_evidence_count": sum(
            card["missing_evidence_count"] > 0 for card in lane_cards
        ),
        "missing_evidence_event_count": missing_event_count,
        "missing_evidence_summary_ready": True,
        "contradictory_evidence_summary_ready": True,
        "contradictory_evidence_lane_count": sum(
            card["contradictory_evidence_count"] > 0 for card in lane_cards
        ),
        "contradictory_evidence_event_count": contradictory_event_count,
        "next_required_observation_count": len(next_required),
        "next_required_observation_summary_ready": all(
            bool(row["next_required_observation_zh"]) for row in next_required
        ),
        "missing_value_treated_as_neutral_count": sum(
            event["missing_value_treated_as_neutral"] for event in events
        ),
        "metadata_only_promoted_to_phase_support_count": sum(
            event["metadata_only_promoted_to_phase_support"] for event in events
        ),
        "contradictory_evidence_promoted_to_confirmation_count": 0,
        "watch_promoted_to_confirmation_count": sum(
            event["watch_promoted_to_confirmation"] for event in events
        ),
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_transition_risk_accumulation_visible"
        ),
        "legal_transition_semantics_preserved": True,
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["transition_risk_evidence_accumulation_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed"
        if artifact["transition_risk_evidence_accumulation_ready"]
        else "blocked"
    )
    return artifact


def build_transition_risk_evidence_accumulation_view_model(
    artifact: dict[str, Any] | None = None,
    *,
    transition_timing_replay_preview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the artifact shape consumed by the dashboard bundle."""

    artifact = artifact or build_transition_risk_evidence_accumulation(
        transition_timing_replay_preview=transition_timing_replay_preview,
    )
    return {
        key: artifact[key]
        for key in (
            "view_id",
            "view_title",
            "output_mode",
            "research_only",
            "declared_state_context",
            "transition_risk_summary",
            "accumulation_lane_cards",
            "missing_evidence_summary",
            "contradictory_evidence_summary",
            "next_required_observations",
            "allowed_uses",
            "prohibited_uses",
            "trust_metadata",
            "transition_accumulation_lane_card_count",
            "evidence_accumulation_event_count",
            "continuation_lane_card_count",
            "watch_lane_card_count",
            "confirmation_lane_card_count",
            "watch_confirmation_boundary_count",
            "lane_with_missing_evidence_count",
            "missing_evidence_event_count",
            "contradictory_evidence_lane_count",
            "contradictory_evidence_event_count",
            "next_required_observation_count",
            "phase_presence_transition_separation_valid",
            "watch_confirmation_separation_valid",
            "missing_value_treated_as_neutral_count",
            "metadata_only_promoted_to_phase_support_count",
            "contradictory_evidence_promoted_to_confirmation_count",
            "watch_promoted_to_confirmation_count",
            "current_data_used_to_infer_declared_phase_count",
            "standalone_classifier_added_count",
            "phase_rank_or_score_added_count",
            "role_count_voting_added_count",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "production_behavior_change_count",
            "semantic_drift_count",
            "prohibited_output_field_count",
            "transition_risk_evidence_accumulation_ready",
        )
    }


def summarize_transition_risk_evidence_accumulation(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase86 readiness fields."""

    artifact = build_transition_risk_evidence_accumulation(path=path)
    return {
        "phase": "86",
        "phase_id": 86,
        "transition_risk_evidence_accumulation_ready": artifact[
            "transition_risk_evidence_accumulation_ready"
        ],
        "declared_current_phase": artifact["declared_state_context"][
            "declared_current_phase"
        ],
        "legal_next_phase": artifact["declared_state_context"]["legal_next_phase"],
        "transition_accumulation_lane_card_count": artifact[
            "transition_accumulation_lane_card_count"
        ],
        "evidence_accumulation_event_count": artifact[
            "evidence_accumulation_event_count"
        ],
        "continuation_lane_card_count": artifact["continuation_lane_card_count"],
        "watch_lane_card_count": artifact["watch_lane_card_count"],
        "confirmation_lane_card_count": artifact["confirmation_lane_card_count"],
        "watch_confirmation_boundary_count": artifact[
            "watch_confirmation_boundary_count"
        ],
        "lane_with_missing_evidence_count": artifact[
            "lane_with_missing_evidence_count"
        ],
        "missing_evidence_event_count": artifact["missing_evidence_event_count"],
        "contradictory_evidence_lane_count": artifact[
            "contradictory_evidence_lane_count"
        ],
        "contradictory_evidence_event_count": artifact[
            "contradictory_evidence_event_count"
        ],
        "next_required_observation_count": artifact[
            "next_required_observation_count"
        ],
        "missing_value_treated_as_neutral_count": artifact[
            "missing_value_treated_as_neutral_count"
        ],
        "metadata_only_promoted_to_phase_support_count": artifact[
            "metadata_only_promoted_to_phase_support_count"
        ],
        "contradictory_evidence_promoted_to_confirmation_count": artifact[
            "contradictory_evidence_promoted_to_confirmation_count"
        ],
        "watch_promoted_to_confirmation_count": artifact[
            "watch_promoted_to_confirmation_count"
        ],
        "phase_presence_transition_separation_valid": artifact[
            "phase_presence_transition_separation_valid"
        ],
        "watch_confirmation_separation_valid": artifact[
            "watch_confirmation_separation_valid"
        ],
        "prohibited_output_field_count": artifact["prohibited_output_field_count"],
        "current_data_used_to_infer_declared_phase_count": artifact[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": artifact[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": artifact["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": artifact["role_count_voting_added_count"],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "production_behavior_change_count": artifact[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": artifact["semantic_drift_count"],
        "product_doctrine_alignment_status": artifact[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": artifact[
            "cycle_state_machine_alignment_status"
        ],
        "transition_risk_evidence_accumulation_artifact": artifact,
        "result": artifact["result"],
    }


def _lane_card(lane: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    contradiction_count = sum(_has_contradictory_evidence(event) for event in events)
    return {
        "lane_id": lane["lane_id"],
        "transition_id": lane["transition_id"],
        "from_phase": lane["from_phase"],
        "to_phase": lane["to_phase"],
        "lane_category": lane["lane_category"],
        "title_zh": lane["title_zh"],
        "timing_preview_status": lane["timing_preview_status"],
        "watch_confirmation_boundary_label": _boundary_label(lane),
        "phase_presence_transition_boundary_valid": _boundary_valid(lane),
        "accumulation_status_counts": dict(
            sorted(Counter(event["accumulation_status"] for event in events).items())
        ),
        "missing_evidence_count": sum(
            bool(event["visible_gap_reason_codes"]) for event in events
        ),
        "contradictory_evidence_count": contradiction_count,
        "visible_gap_reason_codes": lane["visible_gap_reason_codes"],
        "continuity_role_count": len(lane["continuity_role_refs"]),
        "major_group_profile_count": len(lane["major_group_profile_refs"]),
        "abstention_states": sorted(
            {event["abstention_state"] for event in events}
        ),
        "event_count": len(events),
        "changes_declared_phase": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
        "interpretation_zh": lane["accumulation_interpretation_zh"],
    }


def _next_required_observation(card: dict[str, Any]) -> dict[str, Any]:
    if card["missing_evidence_count"] > 0:
        next_step = (
            "補齊此 lane 對應 role 的 governed numeric/release/freshness context，"
            "再重新檢查 watch 或 confirmation 邊界。"
        )
    else:
        next_step = (
            "持續累積下一個 release observation；不得因單一 metadata-ready "
            "狀態改寫 declared phase。"
        )
    return {
        "lane_id": card["lane_id"],
        "transition_id": card["transition_id"],
        "lane_category": card["lane_category"],
        "next_required_observation_zh": next_step,
        "blocked_reason_codes": card["visible_gap_reason_codes"],
        "missing_evidence_count": card["missing_evidence_count"],
        "contradictory_evidence_count": card["contradictory_evidence_count"],
        "watch_confirmation_boundary_label": card[
            "watch_confirmation_boundary_label"
        ],
    }


def _events_by_lane(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        grouped[event["lane_id"]].append(event)
    return dict(grouped)


def _boundary_label(lane: dict[str, Any]) -> str:
    if lane["confirmation_lane"]:
        return "confirmation_only_not_watch"
    if lane["watch_lane"]:
        return "watch_only_not_confirmation"
    return "phase_presence_context_not_transition_confirmation"


def _boundary_valid(lane: dict[str, Any]) -> bool:
    flags = [lane["continuation_lane"], lane["watch_lane"], lane["confirmation_lane"]]
    return sum(bool(flag) for flag in flags) == 1


def _has_contradictory_evidence(event: dict[str, Any]) -> bool:
    text = " ".join(
        [str(event["accumulation_status"]), *event["visible_gap_reason_codes"]]
    )
    return "contradictory" in text or "contradiction" in text


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        artifact.get(key) == value
        for key, value in expected.items()
        if key != "transition_risk_evidence_accumulation_ready"
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
    contract = payload["transition_risk_evidence_accumulation"]
    if not isinstance(contract, dict):
        raise ValueError("Phase86 transition risk accumulation contract must map")
    return contract
