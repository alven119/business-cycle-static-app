"""Phase60 evidence freshness, release timing, and value continuity surface."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_cards,
)
from business_cycle.render.ordered_cycle_transition_lane_templates import (
    build_full_ordered_cycle_transition_lane_templates,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/evidence_freshness_release_value_continuity.yaml"
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
def build_evidence_freshness_release_value_continuity(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the Phase60 research-only continuity artifact."""

    contract = _load_contract(path)
    cards = build_indicator_detail_source_risk_value_cards()
    transition_templates = build_full_ordered_cycle_transition_lane_templates()
    continuity_cards = [_continuity_card(card) for card in cards]
    transition_contexts = [
        _transition_continuity_context(transition)
        for transition in transition_templates["transition_templates"]
    ]
    status_counts = Counter(card["continuity_status"] for card in continuity_cards)
    phase_counts = Counter(card["phase_or_layer"] for card in continuity_cards)
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "60",
        "phase_id": "60",
        "output_mode": contract["policy"]["output_mode"],
        "research_only": True,
        "continuity_cards": continuity_cards,
        "transition_continuity_contexts": transition_contexts,
        "continuity_status_counts": dict(sorted(status_counts.items())),
        "phase_counts": dict(sorted(phase_counts.items())),
        "allowed_uses": contract["dashboard_view_model"]["allowed_uses"],
        "prohibited_uses": contract["dashboard_view_model"]["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "source_indicator_detail_contract": (
                "indicator_detail_source_risk_value_rendering_v1"
            ),
            "source_transition_template_contract": (
                "full_ordered_cycle_transition_lane_templates_v1"
            ),
            "current_data_used_to_infer_declared_phase": False,
            "missing_values_are_neutral": False,
            "metadata_only_is_phase_support": False,
            "phase59_declared_start_governance_deferred": True,
            "production_behavior_change": False,
        },
        "continuity_card_count": len(continuity_cards),
        "phase_count": len(phase_counts),
        "role_with_value_context_count": sum(
            card["value_context_visible"] and bool(card["value_context_status"])
            for card in continuity_cards
        ),
        "role_with_freshness_context_count": sum(
            card["freshness_context_visible"] and bool(card["freshness_context_summary"])
            for card in continuity_cards
        ),
        "role_with_release_timing_context_count": sum(
            card["release_timing_context_visible"]
            and bool(card["release_timing_context"])
            for card in continuity_cards
        ),
        "role_with_continuity_status_count": sum(
            bool(card["continuity_status"]) for card in continuity_cards
        ),
        "stale_or_missing_explanation_count": sum(
            bool(card["stale_or_missing_explanation_zh"])
            for card in continuity_cards
        ),
        "current_numeric_value_available_count": status_counts[
            "current_numeric_value_available"
        ],
        "metadata_ready_value_missing_count": status_counts[
            "metadata_ready_value_missing"
        ],
        "authorized_input_required_count": status_counts[
            "authorized_input_required"
        ],
        "supporting_proxy_only_count": status_counts[
            "supporting_proxy_visible_not_book_core"
        ],
        "source_metadata_incomplete_count": status_counts[
            "source_metadata_incomplete_abstain"
        ],
        "transition_continuity_context_count": len(transition_contexts),
        "transition_lane_context_count": sum(
            context["lane_context_count"] for context in transition_contexts
        ),
        "freshness_context_missing_count": sum(
            not card["freshness_context_visible"] or not card["freshness_context_summary"]
            for card in continuity_cards
        ),
        "release_timing_context_missing_count": sum(
            not card["release_timing_context_visible"]
            or not card["release_timing_context"]
            for card in continuity_cards
        ),
        "value_context_missing_count": sum(
            not card["value_context_visible"] or not card["value_context_status"]
            for card in continuity_cards
        ),
        "declared_phase_age_false_precision_count": 0,
        "phase59_declared_start_governance_deferred": True,
        "missing_value_treated_as_neutral_count": 0,
        "metadata_only_promoted_to_phase_support_count": 0,
        "supporting_proxy_replacement_allowed_count": sum(
            card["supporting_proxy_replacement_allowed"] for card in continuity_cards
        ),
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "evidence_freshness_release_value_continuity_ready"
        ),
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["evidence_freshness_release_value_continuity_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed"
        if artifact["evidence_freshness_release_value_continuity_ready"]
        else "blocked"
    )
    return artifact


@lru_cache(maxsize=1)
def summarize_evidence_freshness_release_value_continuity(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase60 summary fields for scripts and closure checks."""

    artifact = build_evidence_freshness_release_value_continuity(path)
    summary = {
        "phase": "60",
        "phase_id": "60",
        "evidence_freshness_release_value_continuity_ready": artifact[
            "evidence_freshness_release_value_continuity_ready"
        ],
        "continuity_card_count": artifact["continuity_card_count"],
        "phase_count": artifact["phase_count"],
        "role_with_value_context_count": artifact["role_with_value_context_count"],
        "role_with_freshness_context_count": artifact[
            "role_with_freshness_context_count"
        ],
        "role_with_release_timing_context_count": artifact[
            "role_with_release_timing_context_count"
        ],
        "role_with_continuity_status_count": artifact[
            "role_with_continuity_status_count"
        ],
        "stale_or_missing_explanation_count": artifact[
            "stale_or_missing_explanation_count"
        ],
        "current_numeric_value_available_count": artifact[
            "current_numeric_value_available_count"
        ],
        "metadata_ready_value_missing_count": artifact[
            "metadata_ready_value_missing_count"
        ],
        "authorized_input_required_count": artifact["authorized_input_required_count"],
        "supporting_proxy_only_count": artifact["supporting_proxy_only_count"],
        "source_metadata_incomplete_count": artifact[
            "source_metadata_incomplete_count"
        ],
        "transition_continuity_context_count": artifact[
            "transition_continuity_context_count"
        ],
        "transition_lane_context_count": artifact["transition_lane_context_count"],
        "freshness_context_missing_count": artifact[
            "freshness_context_missing_count"
        ],
        "release_timing_context_missing_count": artifact[
            "release_timing_context_missing_count"
        ],
        "value_context_missing_count": artifact["value_context_missing_count"],
        "declared_phase_age_false_precision_count": artifact[
            "declared_phase_age_false_precision_count"
        ],
        "phase59_declared_start_governance_deferred": artifact[
            "phase59_declared_start_governance_deferred"
        ],
        "missing_value_treated_as_neutral_count": artifact[
            "missing_value_treated_as_neutral_count"
        ],
        "metadata_only_promoted_to_phase_support_count": artifact[
            "metadata_only_promoted_to_phase_support_count"
        ],
        "supporting_proxy_replacement_allowed_count": artifact[
            "supporting_proxy_replacement_allowed_count"
        ],
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
        "semantic_drift_count": artifact["semantic_drift_count"],
        "product_doctrine_alignment_status": artifact[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": artifact[
            "cycle_state_machine_alignment_status"
        ],
        "continuity_artifact": artifact,
    }
    summary["result"] = (
        "passed"
        if summary["evidence_freshness_release_value_continuity_ready"]
        else "blocked"
    )
    return summary


def build_evidence_freshness_release_value_continuity_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready research view model for Phase60 continuity."""

    artifact = artifact or build_evidence_freshness_release_value_continuity()
    return {
        "view_id": "evidence_freshness_release_value_continuity",
        "view_title": "Evidence Freshness, Release Timing, and Value Continuity",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "continuity_card_count": artifact["continuity_card_count"],
        "phase_counts": artifact["phase_counts"],
        "continuity_status_counts": artifact["continuity_status_counts"],
        "continuity_cards": artifact["continuity_cards"],
        "transition_continuity_contexts": artifact["transition_continuity_contexts"],
        "trust_metadata": artifact["trust_metadata"],
        "allowed_uses": artifact["allowed_uses"],
        "prohibited_uses": artifact["prohibited_uses"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
    }


def _continuity_card(card: dict[str, Any]) -> dict[str, Any]:
    continuity_status = _continuity_status(card)
    return {
        "role_id": card["role_id"],
        "phase_or_layer": card["phase_or_layer"],
        "phase_label_zh": card["phase_label_zh"],
        "major_group_id": card["major_group_id"],
        "data_risk_level": card["data_risk_level"],
        "source_family": card["source_family"],
        "source_coverage_tier": card["source_coverage_tier"],
        "official_series_ids": card["official_series_ids"],
        "value_context_visible": card["value_context_visible"],
        "value_context_status": card["value_context_status"],
        "freshness_context_visible": card["freshness_context_visible"],
        "freshness_context_summary": card["freshness_context_summary"],
        "release_timing_context_visible": card["release_timing_context_visible"],
        "release_timing_context": card["release_timing_context"],
        "numeric_value_loaded_count": card["numeric_value_loaded_count"],
        "continuity_status": continuity_status,
        "continuity_gap_reason_codes": _gap_reason_codes(card, continuity_status),
        "stale_or_missing_explanation_zh": _stale_or_missing_explanation(
            card,
            continuity_status,
        ),
        "supporting_proxy_only": card["supporting_proxy_only"],
        "supporting_proxy_replacement_allowed": False,
        "user_authorized_input_required": card["user_authorized_input_required"],
        "missing_value_treated_as_neutral": False,
        "metadata_only_promoted_to_phase_support": False,
        "phase_support_added": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
        "allowed_uses": [
            "local_research_dashboard",
            "indicator_value_continuity_review",
            "stale_missing_release_explanation",
        ],
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "phase_score_or_rank_selection",
            "production_decision",
            "portfolio_or_trade_decision",
        ],
    }


def _transition_continuity_context(transition: dict[str, Any]) -> dict[str, Any]:
    lanes = transition["lane_templates"]
    return {
        "transition_id": transition["transition_id"],
        "from_phase": transition["from_phase"],
        "to_phase": transition["to_phase"],
        "legal_next_phase": transition["legal_next_phase"],
        "lane_context_count": len(lanes),
        "requires_freshness_context": True,
        "requires_release_timing_context": True,
        "requires_value_continuity_context": True,
        "declared_phase_age_context_status": (
            "deferred_governed_confirmation_required"
        ),
        "changes_declared_phase": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
    }


def _continuity_status(card: dict[str, Any]) -> str:
    if card["numeric_value_loaded_count"] > 0:
        return "current_numeric_value_available"
    if card["user_authorized_input_required"]:
        return "authorized_input_required"
    if card["supporting_proxy_only"]:
        return "supporting_proxy_visible_not_book_core"
    if card["value_context_status"] == "source_metadata_visible_numeric_cache_missing":
        return "metadata_ready_value_missing"
    return "source_metadata_incomplete_abstain"


def _gap_reason_codes(card: dict[str, Any], continuity_status: str) -> list[str]:
    codes = [continuity_status]
    freshness = card["freshness_context_summary"]
    if freshness.get("stale_or_missing_series_count", 0) > 0:
        codes.append("stale_or_missing_series_visible")
    if card["numeric_value_loaded_count"] == 0:
        codes.append("numeric_value_not_loaded")
    return codes


def _stale_or_missing_explanation(card: dict[str, Any], continuity_status: str) -> str:
    if continuity_status == "current_numeric_value_available":
        return "目前數值已載入；仍需依 release timing 與資料模式標示用途。"
    if continuity_status == "authorized_input_required":
        return "此指標需要授權或使用者自備輸入；未提供前不得補值或推論。"
    if continuity_status == "supporting_proxy_visible_not_book_core":
        return "目前僅能顯示 supporting/proxy context，不能替代 book-core evidence。"
    if continuity_status == "metadata_ready_value_missing":
        return "來源與發布時點 metadata 可見，但目前 numeric cache 尚未載入。"
    return "來源 metadata、current value 或 temporal context 尚不完整，必須保留缺口。"


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        artifact.get(key) == value
        for key, value in expected.items()
        if key != "evidence_freshness_release_value_continuity_ready"
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
    contract = payload["evidence_freshness_release_value_continuity"]
    if not isinstance(contract, dict):
        raise ValueError("Phase60 continuity contract must be a mapping")
    return contract
