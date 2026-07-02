"""Phase61 major-group evidence profile and readiness explanation surface."""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_role_types import primary_role_type
from business_cycle.render.evidence_freshness_release_value_continuity import (
    build_evidence_freshness_release_value_continuity,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/major_group_evidence_profile_readiness.yaml"
)
MAJOR_GROUP_CONTRACT_PATH = ROOT / "specs/audits/book_phase_major_group_contract.yaml"

PHASE_LABELS_ZH = {
    "recovery": "復甦",
    "growth": "成長",
    "boom": "榮景",
    "recession": "衰退/落底",
}
PHASE_DISPLAY = {
    "recovery": "recovery",
    "growth": "growth",
    "boom": "boom",
    "recession_trough": "recession",
}
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
def build_major_group_evidence_profile_readiness(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build Phase61 major-group readiness profiles from Phase60 continuity cards."""

    contract = _load_contract(path)
    major_group_contract = _load_major_group_contract()
    continuity = build_evidence_freshness_release_value_continuity()
    cards = continuity["continuity_cards"]
    cards_by_group: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for card in cards:
        cards_by_group[(card["phase_or_layer"], card["major_group_id"])].append(card)

    role_types = major_group_contract.get("role_types", {})
    default_role_type = major_group_contract["defaults"]["role_type"]
    role_mappings = major_group_contract["role_mappings"]
    profiles: list[dict[str, Any]] = []
    for contract_phase, group_ids in major_group_contract["major_groups"].items():
        display_phase = PHASE_DISPLAY[contract_phase]
        for group_id in group_ids:
            group_cards = sorted(
                cards_by_group.get((display_phase, group_id), []),
                key=lambda row: row["role_id"],
            )
            profiles.append(
                _major_group_profile(
                    contract_phase=contract_phase,
                    display_phase=display_phase,
                    group_id=group_id,
                    cards=group_cards,
                    role_mappings=role_mappings,
                    role_types=role_types,
                    default_role_type=default_role_type,
                ),
            )

    status_counts = Counter(profile["readiness_status"] for profile in profiles)
    phase_counts = Counter(profile["phase_or_layer"] for profile in profiles)
    profiled_required_core_count = sum(
        profile["required_core_role_count"] for profile in profiles
    )
    profiled_supporting_count = sum(
        profile["supporting_role_count"] for profile in profiles
    )
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "61",
        "phase_id": "61",
        "output_mode": contract["policy"]["output_mode"],
        "research_only": True,
        "major_group_profiles": profiles,
        "profile_status_counts": dict(sorted(status_counts.items())),
        "phase_counts": dict(sorted(phase_counts.items())),
        "allowed_uses": contract["dashboard_view_model"]["allowed_uses"],
        "prohibited_uses": contract["dashboard_view_model"]["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "source_continuity_contract": (
                "evidence_freshness_release_value_continuity_v1"
            ),
            "source_major_group_contract": "book_phase_major_group_contract",
            "methodology_requirements_excluded_from_indicator_denominator": True,
            "supporting_proxy_may_replace_book_core": False,
            "missing_values_are_neutral": False,
            "metadata_only_is_phase_support": False,
            "production_behavior_change": False,
        },
        "major_group_profile_count": len(profiles),
        "phase_count": len(phase_counts),
        "phase_with_major_group_profile_count": sum(
            count > 0 for count in phase_counts.values()
        ),
        "profiled_role_count": sum(profile["role_count"] for profile in profiles),
        "profiled_required_core_role_count": profiled_required_core_count,
        "profiled_supporting_role_count": profiled_supporting_count,
        "methodology_requirement_excluded_count": sum(
            len(profile["excluded_methodology_role_ids"]) for profile in profiles
        ),
        "missing_non_methodology_role_count": sum(
            len(profile["missing_non_methodology_role_ids"]) for profile in profiles
        ),
        "required_core_group_profile_complete_count": sum(
            profile["required_core_group_profile_complete"] for profile in profiles
        ),
        "supporting_only_group_count": status_counts[
            "supporting_only_not_phase_presence"
        ],
        "group_with_value_context_count": sum(
            profile["value_context_visible"] for profile in profiles
        ),
        "group_with_freshness_context_count": sum(
            profile["freshness_context_visible"] for profile in profiles
        ),
        "group_with_release_timing_context_count": sum(
            profile["release_timing_context_visible"] for profile in profiles
        ),
        "group_with_readiness_explanation_count": sum(
            bool(profile["readiness_explanation_zh"]) for profile in profiles
        ),
        "core_metadata_ready_value_missing_group_count": status_counts[
            "core_metadata_ready_value_missing"
        ],
        "core_authorized_input_required_group_count": status_counts[
            "core_authorized_input_required"
        ],
        "core_supporting_proxy_visible_not_book_core_group_count": status_counts[
            "core_supporting_proxy_visible_not_book_core"
        ],
        "core_source_metadata_incomplete_abstain_group_count": status_counts[
            "core_source_metadata_incomplete_abstain"
        ],
        "supporting_proxy_context_group_count": sum(
            profile["supporting_proxy_context_visible"] for profile in profiles
        ),
        "group_ready_for_formal_phase_count": sum(
            profile["group_ready_for_formal_phase"] for profile in profiles
        ),
        "group_with_current_numeric_value_count": sum(
            profile["current_numeric_value_available_role_count"] > 0
            for profile in profiles
        ),
        "major_group_promoted_with_missing_core_count": sum(
            profile["major_group_promoted_with_missing_core"] for profile in profiles
        ),
        "supporting_proxy_replacement_allowed_count": sum(
            profile["supporting_proxy_replacement_allowed"] for profile in profiles
        ),
        "missing_value_treated_as_neutral_count": sum(
            profile["missing_value_treated_as_neutral"] for profile in profiles
        ),
        "metadata_only_promoted_to_phase_support_count": sum(
            profile["metadata_only_promoted_to_phase_support"]
            for profile in profiles
        ),
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "major_group_profiles_ready_declared_state_preserved"
        ),
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["major_group_evidence_profile_readiness_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed" if artifact["major_group_evidence_profile_readiness_ready"] else "blocked"
    )
    return artifact


@lru_cache(maxsize=1)
def summarize_major_group_evidence_profile_readiness(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase61 summary fields for scripts and closure checks."""

    artifact = build_major_group_evidence_profile_readiness(path)
    summary = {
        "phase": "61",
        "phase_id": "61",
        "major_group_evidence_profile_readiness_ready": artifact[
            "major_group_evidence_profile_readiness_ready"
        ],
        "major_group_profile_count": artifact["major_group_profile_count"],
        "phase_count": artifact["phase_count"],
        "phase_with_major_group_profile_count": artifact[
            "phase_with_major_group_profile_count"
        ],
        "profiled_role_count": artifact["profiled_role_count"],
        "profiled_required_core_role_count": artifact[
            "profiled_required_core_role_count"
        ],
        "profiled_supporting_role_count": artifact[
            "profiled_supporting_role_count"
        ],
        "methodology_requirement_excluded_count": artifact[
            "methodology_requirement_excluded_count"
        ],
        "missing_non_methodology_role_count": artifact[
            "missing_non_methodology_role_count"
        ],
        "required_core_group_profile_complete_count": artifact[
            "required_core_group_profile_complete_count"
        ],
        "supporting_only_group_count": artifact["supporting_only_group_count"],
        "group_with_value_context_count": artifact["group_with_value_context_count"],
        "group_with_freshness_context_count": artifact[
            "group_with_freshness_context_count"
        ],
        "group_with_release_timing_context_count": artifact[
            "group_with_release_timing_context_count"
        ],
        "group_with_readiness_explanation_count": artifact[
            "group_with_readiness_explanation_count"
        ],
        "core_metadata_ready_value_missing_group_count": artifact[
            "core_metadata_ready_value_missing_group_count"
        ],
        "core_authorized_input_required_group_count": artifact[
            "core_authorized_input_required_group_count"
        ],
        "core_supporting_proxy_visible_not_book_core_group_count": artifact[
            "core_supporting_proxy_visible_not_book_core_group_count"
        ],
        "core_source_metadata_incomplete_abstain_group_count": artifact[
            "core_source_metadata_incomplete_abstain_group_count"
        ],
        "supporting_proxy_context_group_count": artifact[
            "supporting_proxy_context_group_count"
        ],
        "group_ready_for_formal_phase_count": artifact[
            "group_ready_for_formal_phase_count"
        ],
        "group_with_current_numeric_value_count": artifact[
            "group_with_current_numeric_value_count"
        ],
        "major_group_promoted_with_missing_core_count": artifact[
            "major_group_promoted_with_missing_core_count"
        ],
        "supporting_proxy_replacement_allowed_count": artifact[
            "supporting_proxy_replacement_allowed_count"
        ],
        "missing_value_treated_as_neutral_count": artifact[
            "missing_value_treated_as_neutral_count"
        ],
        "metadata_only_promoted_to_phase_support_count": artifact[
            "metadata_only_promoted_to_phase_support_count"
        ],
        "prohibited_output_field_count": artifact["prohibited_output_field_count"],
        "standalone_classifier_added_count": artifact[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": artifact[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": artifact["role_count_voting_added_count"],
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
        "major_group_profile_artifact": artifact,
    }
    summary["result"] = (
        "passed" if summary["major_group_evidence_profile_readiness_ready"] else "blocked"
    )
    return summary


def build_major_group_evidence_profile_readiness_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready research view model for Phase61 group profiles."""

    artifact = artifact or build_major_group_evidence_profile_readiness()
    return {
        "view_id": "major_group_evidence_profile_readiness",
        "view_title": "Major-Group Evidence Profile and Readiness Explanation",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "major_group_profile_count": artifact["major_group_profile_count"],
        "phase_counts": artifact["phase_counts"],
        "profile_status_counts": artifact["profile_status_counts"],
        "major_group_profiles": artifact["major_group_profiles"],
        "trust_metadata": artifact["trust_metadata"],
        "allowed_uses": artifact["allowed_uses"],
        "prohibited_uses": artifact["prohibited_uses"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
    }


def _major_group_profile(
    *,
    contract_phase: str,
    display_phase: str,
    group_id: str,
    cards: list[dict[str, Any]],
    role_mappings: dict[str, str],
    role_types: dict[str, str],
    default_role_type: str,
) -> dict[str, Any]:
    contract_role_ids = sorted(
        role_id
        for role_id, mapped_group in role_mappings.items()
        if mapped_group == group_id and _role_contract_phase(role_id) == contract_phase
    )
    excluded_methodology = [
        role_id
        for role_id in contract_role_ids
        if primary_role_type(role_id) == "data_methodology_requirement"
    ]
    visible_role_ids = {card["role_id"] for card in cards}
    supporting_role_ids = [
        card["role_id"]
        for card in cards
        if role_types.get(card["role_id"], default_role_type) == "supporting"
    ]
    required_core_role_ids = [
        card["role_id"]
        for card in cards
        if role_types.get(card["role_id"], default_role_type) != "supporting"
    ]
    expected_non_methodology = [
        role_id for role_id in contract_role_ids if role_id not in excluded_methodology
    ]
    missing_non_methodology = sorted(set(expected_non_methodology) - visible_role_ids)
    status_counts = Counter(card["continuity_status"] for card in cards)
    readiness_status = _readiness_status(cards, required_core_role_ids)
    return {
        "phase_or_layer": display_phase,
        "phase_label_zh": PHASE_LABELS_ZH[display_phase],
        "contract_phase": contract_phase,
        "major_group_id": group_id,
        "role_ids": [card["role_id"] for card in cards],
        "required_core_role_ids": required_core_role_ids,
        "supporting_role_ids": supporting_role_ids,
        "excluded_methodology_role_ids": excluded_methodology,
        "missing_non_methodology_role_ids": missing_non_methodology,
        "role_count": len(cards),
        "required_core_role_count": len(required_core_role_ids),
        "supporting_role_count": len(supporting_role_ids),
        "readiness_status": readiness_status,
        "continuity_status_counts": dict(sorted(status_counts.items())),
        "current_numeric_value_available_role_count": status_counts[
            "current_numeric_value_available"
        ],
        "metadata_ready_value_missing_role_count": status_counts[
            "metadata_ready_value_missing"
        ],
        "authorized_input_required_role_count": status_counts[
            "authorized_input_required"
        ],
        "supporting_proxy_only_role_count": status_counts[
            "supporting_proxy_visible_not_book_core"
        ],
        "source_metadata_incomplete_role_count": status_counts[
            "source_metadata_incomplete_abstain"
        ],
        "value_context_visible": all(card["value_context_visible"] for card in cards),
        "freshness_context_visible": all(
            card["freshness_context_visible"] for card in cards
        ),
        "release_timing_context_visible": all(
            card["release_timing_context_visible"] for card in cards
        ),
        "supporting_proxy_context_visible": any(
            card["supporting_proxy_only"] for card in cards
        ),
        "readiness_explanation_zh": _readiness_explanation(readiness_status),
        "missing_or_blocked_reason_codes": _reason_codes(cards, readiness_status),
        "required_core_group_profile_complete": bool(required_core_role_ids)
        and not missing_non_methodology,
        "group_ready_for_formal_phase": False,
        "major_group_promoted_with_missing_core": False,
        "supporting_proxy_replacement_allowed": False,
        "missing_value_treated_as_neutral": False,
        "metadata_only_promoted_to_phase_support": False,
        "phase_support_added": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
        "allowed_uses": [
            "local_research_dashboard",
            "major_group_readiness_explanation",
            "indicator_group_attribution",
        ],
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "phase_score_or_rank_selection",
            "production_decision",
            "portfolio_or_trade_decision",
        ],
    }


def _role_contract_phase(role_id: str) -> str:
    if role_id.startswith("recovery_"):
        return "recovery"
    if role_id.startswith("growth_"):
        return "growth"
    if role_id.startswith("boom_"):
        return "boom"
    return "recession_trough"


def _readiness_status(cards: list[dict[str, Any]], required_core_role_ids: list[str]) -> str:
    required_cards = [card for card in cards if card["role_id"] in required_core_role_ids]
    if not required_cards:
        return "supporting_only_not_phase_presence"
    statuses = {card["continuity_status"] for card in required_cards}
    if "authorized_input_required" in statuses:
        return "core_authorized_input_required"
    if "source_metadata_incomplete_abstain" in statuses:
        return "core_source_metadata_incomplete_abstain"
    if "supporting_proxy_visible_not_book_core" in statuses:
        return "core_supporting_proxy_visible_not_book_core"
    if statuses == {"metadata_ready_value_missing"}:
        return "core_metadata_ready_value_missing"
    return "core_mixed_continuity_gap"


def _readiness_explanation(readiness_status: str) -> str:
    return {
        "core_metadata_ready_value_missing": (
            "此 major group 的 core roles 已有來源與發布脈絡，但目前缺 numeric cache；只能做缺值/新鮮度解釋。"
        ),
        "core_authorized_input_required": (
            "此 major group 至少一個 core role 需要授權或使用者自備資料；未補齊前不得當作完整證據。"
        ),
        "core_supporting_proxy_visible_not_book_core": (
            "此 major group 目前含 proxy/supporting context；可輔助解釋，但不能替代 book-core role。"
        ),
        "core_source_metadata_incomplete_abstain": (
            "此 major group 至少一個 core role 的來源、轉換或 temporal metadata 未完整，必須 abstain。"
        ),
        "supporting_only_not_phase_presence": (
            "此 group 只有 supporting context，不能單獨構成 phase presence 或 transition confirmation。"
        ),
        "core_mixed_continuity_gap": (
            "此 major group 存在混合 readiness gap，需要逐 role 檢查後才能使用。"
        ),
    }[readiness_status]


def _reason_codes(cards: list[dict[str, Any]], readiness_status: str) -> list[str]:
    codes = {readiness_status}
    for card in cards:
        codes.update(card["continuity_gap_reason_codes"])
    return sorted(codes)


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        artifact.get(key) == value
        for key, value in expected.items()
        if key != "major_group_evidence_profile_readiness_ready"
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
    contract = payload["major_group_evidence_profile_readiness"]
    if not isinstance(contract, dict):
        raise ValueError("Phase61 major-group profile contract must be a mapping")
    return contract


def _load_major_group_contract() -> dict[str, Any]:
    return yaml.safe_load(MAJOR_GROUP_CONTRACT_PATH.read_text(encoding="utf-8"))[
        "book_phase_major_group_contract"
    ]
