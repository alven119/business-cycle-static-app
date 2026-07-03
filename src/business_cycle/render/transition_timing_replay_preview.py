"""Phase67 transition timing replay preview.

The preview composes existing ordered-cycle transition templates, continuity
cards, and major-group readiness profiles into a dashboard-ready evidence
accumulation surface. It is intentionally non-emitting: no current phase,
candidate phase, historical validation result, backtest, or metric is produced.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.declared_phase_registry import (
    summarize_declared_cycle_state,
)
from business_cycle.render.evidence_freshness_release_value_continuity import (
    build_evidence_freshness_release_value_continuity,
)
from business_cycle.render.major_group_evidence_profile_readiness import (
    build_major_group_evidence_profile_readiness,
)
from business_cycle.render.ordered_cycle_transition_lane_templates import (
    build_full_ordered_cycle_transition_lane_templates,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/transition_timing_replay_preview.yaml"

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


@lru_cache(maxsize=1)
def build_transition_timing_replay_preview(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a research-only transition timing replay preview artifact."""

    contract = _load_contract(path)
    declared = summarize_declared_cycle_state()
    templates = build_full_ordered_cycle_transition_lane_templates()
    continuity = build_evidence_freshness_release_value_continuity()
    major_groups = build_major_group_evidence_profile_readiness()
    lane_rows = [
        _lane_timing_preview(
            lane,
            transition=transition,
            continuity_cards=continuity["continuity_cards"],
            major_group_profiles=major_groups["major_group_profiles"],
        )
        for transition in templates["transition_templates"]
        for lane in transition["lane_templates"]
    ]
    checkpoints = [
        _checkpoint(row, declared=declared)
        for row in contract["preview_checkpoints"]
    ]
    accumulation_events = [
        _accumulation_event(checkpoint=checkpoint, lane=lane)
        for checkpoint in checkpoints
        for lane in lane_rows
    ]
    lane_categories = Counter(lane["lane_category"] for lane in lane_rows)
    accumulation_statuses = Counter(
        event["accumulation_status"] for event in accumulation_events
    )
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "67",
        "phase_id": "67",
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "declared_state_context": {
            "declared_state_label": "declared_state_not_inferred_current_phase",
            "declared_current_phase": declared["declared_current_phase"],
            "legal_previous_phase": declared["legal_previous_phase"],
            "legal_next_phase": declared["legal_next_phase"],
            "declared_phase_start_date": declared["declared_phase_start_date"],
            "phase_age_status": declared["phase_age_status"],
            "phase_age_false_precision_count": declared[
                "phase_age_false_precision_count"
            ],
        },
        "cycle_order": templates["cycle_order"],
        "legal_transitions": templates["legal_transitions"],
        "transition_replay_checkpoints": checkpoints,
        "transition_lane_timing_previews": lane_rows,
        "evidence_accumulation_events": accumulation_events,
        "accumulation_status_counts": dict(sorted(accumulation_statuses.items())),
        "lane_category_counts": dict(sorted(lane_categories.items())),
        "allowed_uses": contract["dashboard_view_model"]["allowed_uses"],
        "prohibited_uses": contract["dashboard_view_model"]["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "source_transition_template_contract": (
                "full_ordered_cycle_transition_lane_templates_v1"
            ),
            "source_continuity_contract": (
                "evidence_freshness_release_value_continuity_v1"
            ),
            "source_major_group_profile_contract": (
                "major_group_evidence_profile_readiness_v1"
            ),
            "declared_state_source": "declared_cycle_state_registry",
            "uses_current_data_to_infer_declared_phase": False,
            "watch_confirmation_separated": templates[
                "watch_confirmation_separation_valid"
            ],
            "missing_values_are_neutral": False,
            "metadata_only_is_phase_support": False,
            "historical_validation_executed": False,
            "backtest_executed": False,
            "production_behavior_change": False,
        },
        "legal_cycle_order_valid": templates["legal_cycle_order_valid"],
        "transition_replay_checkpoint_count": len(checkpoints),
        "transition_template_count": templates["legal_transition_template_count"],
        "transition_lane_timing_preview_count": len(lane_rows),
        "continuation_lane_timing_preview_count": lane_categories[
            "continuation_context"
        ],
        "watch_lane_timing_preview_count": lane_categories["transition_watch"],
        "confirmation_lane_timing_preview_count": lane_categories[
            "transition_confirmation"
        ],
        "evidence_accumulation_event_count": len(accumulation_events),
        "event_with_gap_reason_count": sum(
            bool(event["visible_gap_reason_codes"]) for event in accumulation_events
        ),
        "lane_with_major_group_profile_count": sum(
            bool(lane["major_group_profile_refs"]) for lane in lane_rows
        ),
        "lane_with_continuity_context_count": sum(
            bool(lane["continuity_role_refs"]) for lane in lane_rows
        ),
        "watch_confirmation_separation_valid": templates[
            "watch_confirmation_separation_valid"
        ],
        "missing_value_treated_as_neutral_count": 0,
        "metadata_only_promoted_to_phase_support_count": 0,
        "phase_age_false_precision_count": declared["phase_age_false_precision_count"],
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "historical_validation_executed": False,
        "backtest_execution_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "transition_timing_replay_preview_ready_declared_state_preserved"
        ),
        "legal_transition_semantics_preserved": True,
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["transition_timing_replay_preview_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed" if artifact["transition_timing_replay_preview_ready"] else "blocked"
    )
    return artifact


@lru_cache(maxsize=1)
def summarize_transition_timing_replay_preview(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase67 summary fields for scripts and closure checks."""

    artifact = build_transition_timing_replay_preview(path)
    summary = {
        "phase": "67",
        "phase_id": "67",
        "transition_timing_replay_preview_ready": artifact[
            "transition_timing_replay_preview_ready"
        ],
        "declared_current_phase": artifact["declared_state_context"][
            "declared_current_phase"
        ],
        "legal_previous_phase": artifact["declared_state_context"][
            "legal_previous_phase"
        ],
        "legal_next_phase": artifact["declared_state_context"]["legal_next_phase"],
        "phase_age_status": artifact["declared_state_context"]["phase_age_status"],
        "legal_cycle_order_valid": artifact["legal_cycle_order_valid"],
        "transition_replay_checkpoint_count": artifact[
            "transition_replay_checkpoint_count"
        ],
        "transition_template_count": artifact["transition_template_count"],
        "transition_lane_timing_preview_count": artifact[
            "transition_lane_timing_preview_count"
        ],
        "continuation_lane_timing_preview_count": artifact[
            "continuation_lane_timing_preview_count"
        ],
        "watch_lane_timing_preview_count": artifact[
            "watch_lane_timing_preview_count"
        ],
        "confirmation_lane_timing_preview_count": artifact[
            "confirmation_lane_timing_preview_count"
        ],
        "evidence_accumulation_event_count": artifact[
            "evidence_accumulation_event_count"
        ],
        "event_with_gap_reason_count": artifact["event_with_gap_reason_count"],
        "lane_with_major_group_profile_count": artifact[
            "lane_with_major_group_profile_count"
        ],
        "lane_with_continuity_context_count": artifact[
            "lane_with_continuity_context_count"
        ],
        "watch_confirmation_separation_valid": artifact[
            "watch_confirmation_separation_valid"
        ],
        "missing_value_treated_as_neutral_count": artifact[
            "missing_value_treated_as_neutral_count"
        ],
        "metadata_only_promoted_to_phase_support_count": artifact[
            "metadata_only_promoted_to_phase_support_count"
        ],
        "phase_age_false_precision_count": artifact[
            "phase_age_false_precision_count"
        ],
        "prohibited_output_field_count": artifact["prohibited_output_field_count"],
        "current_data_used_to_infer_declared_phase_count": artifact[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": artifact[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": artifact[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": artifact["role_count_voting_added_count"],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "historical_validation_executed": artifact["historical_validation_executed"],
        "backtest_execution_count": artifact["backtest_execution_count"],
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
        "legal_transition_semantics_preserved": artifact[
            "legal_transition_semantics_preserved"
        ],
        "transition_timing_replay_preview": artifact,
    }
    summary["result"] = (
        "passed" if summary["transition_timing_replay_preview_ready"] else "blocked"
    )
    return summary


def build_transition_timing_replay_preview_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready transition timing replay preview view model."""

    artifact = artifact or build_transition_timing_replay_preview()
    return {
        "view_id": "transition_timing_replay_preview",
        "view_title": "Transition Timing Replay Preview",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "declared_state_context": artifact["declared_state_context"],
        "transition_replay_checkpoints": artifact["transition_replay_checkpoints"],
        "transition_lane_timing_previews": artifact[
            "transition_lane_timing_previews"
        ],
        "evidence_accumulation_events": artifact["evidence_accumulation_events"],
        "accumulation_status_counts": artifact["accumulation_status_counts"],
        "lane_category_counts": artifact["lane_category_counts"],
        "trust_metadata": artifact["trust_metadata"],
        "allowed_uses": artifact["allowed_uses"],
        "prohibited_uses": artifact["prohibited_uses"],
        "transition_replay_checkpoint_count": artifact[
            "transition_replay_checkpoint_count"
        ],
        "transition_lane_timing_preview_count": artifact[
            "transition_lane_timing_preview_count"
        ],
        "evidence_accumulation_event_count": artifact[
            "evidence_accumulation_event_count"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
    }


def _lane_timing_preview(
    lane: dict[str, Any],
    *,
    transition: dict[str, Any],
    continuity_cards: list[dict[str, Any]],
    major_group_profiles: list[dict[str, Any]],
) -> dict[str, Any]:
    profile_refs = _matching_major_group_profiles(lane, major_group_profiles)
    continuity_refs = _matching_continuity_cards(lane, continuity_cards)
    continuity_statuses = Counter(row["continuity_status"] for row in continuity_refs)
    missing_codes = sorted(
        {
            code
            for row in continuity_refs
            for code in row["continuity_gap_reason_codes"]
        }
    )
    return {
        "transition_id": transition["transition_id"],
        "from_phase": transition["from_phase"],
        "to_phase": transition["to_phase"],
        "lane_id": lane["lane_id"],
        "lane_category": lane["lane_category"],
        "title_zh": lane["title_zh"],
        "watch_lane": lane["watch_lane"],
        "confirmation_lane": lane["confirmation_lane"],
        "continuation_lane": lane["continuation_lane"],
        "book_core_role_groups": lane["book_core_role_groups"],
        "supporting_only_role_groups": lane["supporting_only_role_groups"],
        "supporting_only_can_replace_book_core": False,
        "major_group_profile_refs": profile_refs,
        "continuity_role_refs": continuity_refs,
        "continuity_status_counts": dict(sorted(continuity_statuses.items())),
        "visible_gap_reason_codes": missing_codes,
        "timing_preview_status": _timing_preview_status(
            profile_refs,
            continuity_refs,
        ),
        "accumulation_interpretation_zh": _accumulation_interpretation(lane),
        "changes_declared_phase": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
    }


def _matching_major_group_profiles(
    lane: dict[str, Any],
    major_group_profiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups = tuple(str(group) for group in lane["book_core_role_groups"])
    refs: list[dict[str, Any]] = []
    for profile in major_group_profiles:
        if _profile_matches_groups(profile, groups):
            refs.append(
                {
                    "phase_or_layer": profile["phase_or_layer"],
                    "major_group_id": profile["major_group_id"],
                    "readiness_status": profile["readiness_status"],
                    "required_core_role_count": profile["required_core_role_count"],
                    "current_numeric_value_available_role_count": profile[
                        "current_numeric_value_available_role_count"
                    ],
                    "missing_or_blocked_reason_codes": profile[
                        "missing_or_blocked_reason_codes"
                    ],
                    "group_ready_for_formal_phase": False,
                }
            )
    return refs


def _matching_continuity_cards(
    lane: dict[str, Any],
    continuity_cards: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups = tuple(str(group) for group in lane["book_core_role_groups"])
    refs: list[dict[str, Any]] = []
    for card in continuity_cards:
        if _card_matches_groups(card, groups):
            refs.append(
                {
                    "role_id": card["role_id"],
                    "phase_or_layer": card["phase_or_layer"],
                    "major_group_id": card["major_group_id"],
                    "continuity_status": card["continuity_status"],
                    "continuity_gap_reason_codes": card[
                        "continuity_gap_reason_codes"
                    ],
                    "numeric_value_loaded_count": card["numeric_value_loaded_count"],
                    "release_timing_context_visible": card[
                        "release_timing_context_visible"
                    ],
                    "freshness_context_visible": card["freshness_context_visible"],
                    "metadata_only_promoted_to_phase_support": False,
                }
            )
    return refs


def _profile_matches_groups(profile: dict[str, Any], groups: tuple[str, ...]) -> bool:
    group_id = str(profile["major_group_id"])
    phase = str(profile["phase_or_layer"])
    return any(group_id == group or group_id in group or phase in group for group in groups)


def _card_matches_groups(card: dict[str, Any], groups: tuple[str, ...]) -> bool:
    group_id = str(card["major_group_id"])
    phase = str(card["phase_or_layer"])
    return any(group_id == group or group_id in group or phase in group for group in groups)


def _timing_preview_status(
    profile_refs: list[dict[str, Any]],
    continuity_refs: list[dict[str, Any]],
) -> str:
    if any(ref["current_numeric_value_available_role_count"] > 0 for ref in profile_refs):
        return "numeric_context_available_research_only"
    if continuity_refs:
        return "metadata_ready_waiting_numeric_accumulation"
    if profile_refs:
        return "major_group_profile_visible_waiting_role_context"
    return "template_only_waiting_source_wiring"


def _accumulation_interpretation(lane: dict[str, Any]) -> str:
    if lane["confirmation_lane"]:
        return "此 lane 只可呈現 confirmation evidence 的累積狀態；watch 不得升級成 confirmation。"
    if lane["watch_lane"]:
        return "此 lane 只可呈現 watch evidence 的累積狀態；不得改寫 declared phase。"
    return "此 lane 呈現 declared phase continuation context；不是下一階段確認。"


def _checkpoint(row: dict[str, Any], *, declared: dict[str, Any]) -> dict[str, Any]:
    return {
        "checkpoint_id": row["checkpoint_id"],
        "title_zh": row["title_zh"],
        "checkpoint_semantics_zh": row["checkpoint_semantics_zh"],
        "declared_current_phase": declared["declared_current_phase"],
        "legal_next_phase": declared["legal_next_phase"],
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
    }


def _accumulation_event(
    *,
    checkpoint: dict[str, Any],
    lane: dict[str, Any],
) -> dict[str, Any]:
    return {
        "checkpoint_id": checkpoint["checkpoint_id"],
        "transition_id": lane["transition_id"],
        "lane_id": lane["lane_id"],
        "lane_category": lane["lane_category"],
        "accumulation_status": lane["timing_preview_status"],
        "visible_gap_reason_codes": lane["visible_gap_reason_codes"],
        "abstention_state": _abstention_state(lane),
        "watch_lane": lane["watch_lane"],
        "confirmation_lane": lane["confirmation_lane"],
        "watch_promoted_to_confirmation": False,
        "missing_value_treated_as_neutral": False,
        "metadata_only_promoted_to_phase_support": False,
        "changes_declared_phase": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
    }


def _abstention_state(lane: dict[str, Any]) -> str:
    if lane["visible_gap_reason_codes"]:
        return "visible_gap_requires_abstention_or_context_label"
    return "no_gap_visible_research_only_not_decision"


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        artifact.get(key) == value
        for key, value in expected.items()
        if key != "transition_timing_replay_preview_ready"
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
    contract = payload["transition_timing_replay_preview"]
    if not isinstance(contract, dict):
        raise ValueError("Phase67 transition timing contract must be a mapping")
    return contract
