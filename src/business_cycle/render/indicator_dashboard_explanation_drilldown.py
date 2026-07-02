"""Phase62 indicator-to-dashboard explanation drill-down surface."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.evidence_freshness_release_value_continuity import (
    build_evidence_freshness_release_value_continuity,
)
from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_cards,
)
from business_cycle.render.major_group_evidence_profile_readiness import (
    build_major_group_evidence_profile_readiness,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/indicator_dashboard_explanation_drilldown.yaml"
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
def build_indicator_dashboard_explanation_drilldown(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build Phase62 research-only dashboard drill-down artifact."""

    contract = _load_contract(path)
    indicator_cards = build_indicator_detail_source_risk_value_cards()
    continuity = build_evidence_freshness_release_value_continuity()
    major_groups = build_major_group_evidence_profile_readiness()
    continuity_by_role = {
        card["role_id"]: card for card in continuity["continuity_cards"]
    }
    role_drilldowns = [
        _role_drilldown(
            indicator_card=card,
            continuity_card=continuity_by_role[card["role_id"]],
        )
        for card in sorted(indicator_cards, key=lambda item: item["role_id"])
    ]
    role_by_id = {role["role_id"]: role for role in role_drilldowns}
    major_group_drilldowns = [
        _major_group_drilldown(profile, role_by_id=role_by_id)
        for profile in major_groups["major_group_profiles"]
    ]
    phase_counts = Counter(role["phase_or_layer"] for role in role_drilldowns)
    continuity_counts = Counter(role["continuity_status"] for role in role_drilldowns)
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "62",
        "phase_id": "62",
        "output_mode": contract["policy"]["output_mode"],
        "research_only": True,
        "major_group_drilldowns": major_group_drilldowns,
        "role_drilldowns": role_drilldowns,
        "phase_counts": dict(sorted(phase_counts.items())),
        "continuity_status_counts": dict(sorted(continuity_counts.items())),
        "allowed_uses": contract["dashboard_view_model"]["allowed_uses"],
        "prohibited_uses": contract["dashboard_view_model"]["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "source_indicator_detail_contract": (
                "indicator_detail_source_risk_value_rendering_v1"
            ),
            "source_continuity_contract": (
                "evidence_freshness_release_value_continuity_v1"
            ),
            "source_major_group_profile_contract": (
                "major_group_evidence_profile_readiness_v1"
            ),
            "current_data_used_to_infer_declared_phase": False,
            "missing_values_are_neutral": False,
            "metadata_only_is_phase_support": False,
            "supporting_proxy_may_replace_book_core": False,
            "production_behavior_change": False,
        },
        "major_group_drilldown_count": len(major_group_drilldowns),
        "role_drilldown_count": len(role_drilldowns),
        "phase_count": len(phase_counts),
        "phase_with_drilldown_count": sum(count > 0 for count in phase_counts.values()),
        "role_with_source_detail_count": _present_count(
            role_drilldowns,
            "source_detail",
        ),
        "role_with_release_timing_detail_count": _present_count(
            role_drilldowns,
            "release_timing_detail",
        ),
        "role_with_freshness_detail_count": _present_count(
            role_drilldowns,
            "freshness_detail",
        ),
        "role_with_transformation_detail_count": _present_count(
            role_drilldowns,
            "transformation_detail",
        ),
        "role_with_rule_or_usability_detail_count": _present_count(
            role_drilldowns,
            "rule_or_usability_detail",
        ),
        "role_with_provenance_detail_count": _present_count(
            role_drilldowns,
            "provenance_detail",
        ),
        "role_with_data_mode_detail_count": _present_count(
            role_drilldowns,
            "data_mode_detail",
        ),
        "role_with_abstention_reason_count": _present_count(
            role_drilldowns,
            "abstention_reason_detail",
        ),
        "role_with_dashboard_explanation_count": sum(
            bool(role["dashboard_explanation_zh"]) for role in role_drilldowns
        ),
        "role_with_drilldown_href_count": sum(
            bool(role["drilldown_href"]) for role in role_drilldowns
        ),
        "major_group_with_role_links_count": sum(
            bool(group["role_links"]) for group in major_group_drilldowns
        ),
        "major_group_with_readiness_explanation_count": sum(
            bool(group["readiness_explanation_zh"])
            for group in major_group_drilldowns
        ),
        "official_source_role_drilldown_count": sum(
            bool(role["source_detail"]["official_series_ids"])
            for role in role_drilldowns
        ),
        "authorized_input_drilldown_count": sum(
            role["user_authorized_input_required"] for role in role_drilldowns
        ),
        "supporting_proxy_drilldown_count": sum(
            role["supporting_proxy_only"] for role in role_drilldowns
        ),
        "metadata_ready_value_missing_drilldown_count": continuity_counts[
            "metadata_ready_value_missing"
        ],
        "source_metadata_incomplete_drilldown_count": continuity_counts[
            "source_metadata_incomplete_abstain"
        ],
        "current_numeric_value_available_drilldown_count": continuity_counts[
            "current_numeric_value_available"
        ],
        "group_ready_for_formal_phase_count": sum(
            group["group_ready_for_formal_phase"] for group in major_group_drilldowns
        ),
        "source_rule_provenance_complete": all(
            _role_source_rule_provenance_complete(role) for role in role_drilldowns
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
            "indicator_dashboard_drilldown_ready_declared_state_preserved"
        ),
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["indicator_dashboard_explanation_drilldown_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed"
        if artifact["indicator_dashboard_explanation_drilldown_ready"]
        else "blocked"
    )
    return artifact


@lru_cache(maxsize=1)
def summarize_indicator_dashboard_explanation_drilldown(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase62 summary fields for scripts and closure checks."""

    artifact = build_indicator_dashboard_explanation_drilldown(path)
    summary = {
        "phase": "62",
        "phase_id": "62",
        "indicator_dashboard_explanation_drilldown_ready": artifact[
            "indicator_dashboard_explanation_drilldown_ready"
        ],
        "major_group_drilldown_count": artifact["major_group_drilldown_count"],
        "role_drilldown_count": artifact["role_drilldown_count"],
        "phase_count": artifact["phase_count"],
        "phase_with_drilldown_count": artifact["phase_with_drilldown_count"],
        "role_with_source_detail_count": artifact["role_with_source_detail_count"],
        "role_with_release_timing_detail_count": artifact[
            "role_with_release_timing_detail_count"
        ],
        "role_with_freshness_detail_count": artifact[
            "role_with_freshness_detail_count"
        ],
        "role_with_transformation_detail_count": artifact[
            "role_with_transformation_detail_count"
        ],
        "role_with_rule_or_usability_detail_count": artifact[
            "role_with_rule_or_usability_detail_count"
        ],
        "role_with_provenance_detail_count": artifact[
            "role_with_provenance_detail_count"
        ],
        "role_with_data_mode_detail_count": artifact[
            "role_with_data_mode_detail_count"
        ],
        "role_with_abstention_reason_count": artifact[
            "role_with_abstention_reason_count"
        ],
        "role_with_dashboard_explanation_count": artifact[
            "role_with_dashboard_explanation_count"
        ],
        "role_with_drilldown_href_count": artifact[
            "role_with_drilldown_href_count"
        ],
        "major_group_with_role_links_count": artifact[
            "major_group_with_role_links_count"
        ],
        "major_group_with_readiness_explanation_count": artifact[
            "major_group_with_readiness_explanation_count"
        ],
        "official_source_role_drilldown_count": artifact[
            "official_source_role_drilldown_count"
        ],
        "authorized_input_drilldown_count": artifact[
            "authorized_input_drilldown_count"
        ],
        "supporting_proxy_drilldown_count": artifact[
            "supporting_proxy_drilldown_count"
        ],
        "metadata_ready_value_missing_drilldown_count": artifact[
            "metadata_ready_value_missing_drilldown_count"
        ],
        "source_metadata_incomplete_drilldown_count": artifact[
            "source_metadata_incomplete_drilldown_count"
        ],
        "current_numeric_value_available_drilldown_count": artifact[
            "current_numeric_value_available_drilldown_count"
        ],
        "group_ready_for_formal_phase_count": artifact[
            "group_ready_for_formal_phase_count"
        ],
        "source_rule_provenance_complete": artifact[
            "source_rule_provenance_complete"
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
        "drilldown_artifact": artifact,
    }
    summary["result"] = (
        "passed"
        if summary["indicator_dashboard_explanation_drilldown_ready"]
        else "blocked"
    )
    return summary


def build_indicator_dashboard_explanation_drilldown_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready research view model for Phase62 drill-down."""

    artifact = artifact or build_indicator_dashboard_explanation_drilldown()
    return {
        "view_id": "indicator_dashboard_explanation_drilldown",
        "view_title": "Indicator-to-Dashboard Explanation Drill-down",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "major_group_drilldown_count": artifact["major_group_drilldown_count"],
        "role_drilldown_count": artifact["role_drilldown_count"],
        "phase_counts": artifact["phase_counts"],
        "continuity_status_counts": artifact["continuity_status_counts"],
        "major_group_drilldowns": artifact["major_group_drilldowns"],
        "role_drilldowns": artifact["role_drilldowns"],
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


def _role_drilldown(
    *,
    indicator_card: dict[str, Any],
    continuity_card: dict[str, Any],
) -> dict[str, Any]:
    role_id = indicator_card["role_id"]
    return {
        "drilldown_id": f"role_drilldown:{role_id}",
        "role_id": role_id,
        "phase_or_layer": indicator_card["phase_or_layer"],
        "phase_label_zh": indicator_card["phase_label_zh"],
        "major_group_id": indicator_card["major_group_id"],
        "continuity_status": continuity_card["continuity_status"],
        "source_detail": {
            "source_family": indicator_card["source_family"],
            "source_coverage_tier": indicator_card["source_coverage_tier"],
            "source_risk_label_zh": indicator_card["source_risk_label_zh"],
            "data_risk_level": indicator_card["data_risk_level"],
            "substitution_degree": indicator_card["substitution_degree"],
            "official_series_ids": indicator_card["official_series_ids"],
            "latest_observation_context": indicator_card[
                "latest_observation_context"
            ],
        },
        "release_timing_detail": continuity_card["release_timing_context"],
        "freshness_detail": continuity_card["freshness_context_summary"],
        "transformation_detail": {
            "transformation_context_visible": indicator_card[
                "transformation_context_visible"
            ],
            "transformation_semantics_status": indicator_card[
                "transformation_semantics_status"
            ],
        },
        "rule_or_usability_detail": {
            "coverage_status": indicator_card["coverage_status"],
            "dashboard_display_status": indicator_card["dashboard_display_status"],
            "evidence_usability_status": indicator_card[
                "evidence_usability_status"
            ],
            "book_core_replacement_allowed": indicator_card[
                "book_core_replacement_allowed"
            ],
            "supporting_proxy_can_replace_book_core": False,
            "phase_support_added": False,
            "candidate_selection_eligible": False,
        },
        "provenance_detail": {
            "source_indicator_detail_contract": (
                "indicator_detail_source_risk_value_rendering_v1"
            ),
            "source_continuity_contract": (
                "evidence_freshness_release_value_continuity_v1"
            ),
            "source_major_group_profile_contract": (
                "major_group_evidence_profile_readiness_v1"
            ),
            "source_series_count": len(indicator_card["official_series_ids"]),
            "data_mode": _data_mode_detail(indicator_card),
            "research_only": True,
        },
        "data_mode_detail": _data_mode_detail(indicator_card),
        "abstention_reason_detail": {
            "why_not_evidence_zh": indicator_card["why_not_evidence_zh"],
            "stale_or_missing_explanation_zh": continuity_card[
                "stale_or_missing_explanation_zh"
            ],
            "continuity_gap_reason_codes": continuity_card[
                "continuity_gap_reason_codes"
            ],
        },
        "dashboard_explanation_zh": indicator_card["dashboard_explanation_zh"],
        "next_gap_zh": indicator_card["next_gap_zh"],
        "drilldown_href": f"#role-{role_id}",
        "user_authorized_input_required": indicator_card[
            "user_authorized_input_required"
        ],
        "supporting_proxy_only": indicator_card["supporting_proxy_only"],
        "missing_value_treated_as_neutral": False,
        "metadata_only_promoted_to_phase_support": False,
        "supporting_proxy_replacement_allowed": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
        "allowed_uses": [
            "local_research_dashboard",
            "indicator_explanation_drilldown",
            "source_release_transformation_review",
        ],
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "phase_score_or_rank_selection",
            "production_decision",
            "portfolio_or_trade_decision",
        ],
    }


def _major_group_drilldown(
    profile: dict[str, Any],
    *,
    role_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    role_links = [
        {
            "role_id": role_id,
            "role_drilldown_id": role_by_id[role_id]["drilldown_id"],
            "drilldown_href": role_by_id[role_id]["drilldown_href"],
            "continuity_status": role_by_id[role_id]["continuity_status"],
            "data_risk_level": role_by_id[role_id]["source_detail"][
                "data_risk_level"
            ],
        }
        for role_id in profile["role_ids"]
        if role_id in role_by_id
    ]
    return {
        "major_group_drilldown_id": (
            f"major_group_drilldown:{profile['phase_or_layer']}:{profile['major_group_id']}"
        ),
        "phase_or_layer": profile["phase_or_layer"],
        "phase_label_zh": profile["phase_label_zh"],
        "major_group_id": profile["major_group_id"],
        "readiness_status": profile["readiness_status"],
        "readiness_explanation_zh": profile["readiness_explanation_zh"],
        "required_core_role_ids": profile["required_core_role_ids"],
        "supporting_role_ids": profile["supporting_role_ids"],
        "excluded_methodology_role_ids": profile["excluded_methodology_role_ids"],
        "missing_non_methodology_role_ids": profile[
            "missing_non_methodology_role_ids"
        ],
        "role_links": role_links,
        "role_drilldown_count": len(role_links),
        "group_ready_for_formal_phase": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
        "allowed_uses": profile["allowed_uses"],
        "prohibited_uses": profile["prohibited_uses"],
    }


def _data_mode_detail(indicator_card: dict[str, Any]) -> dict[str, Any]:
    source_modes = sorted(
        {
            str(item.get("source_mode", "unknown"))
            for item in indicator_card["latest_observation_context"]
        },
    )
    return {
        "display_data_mode": "current_research_metadata_or_fixture",
        "point_in_time_result": False,
        "revised_diagnostic_only": True,
        "source_modes": source_modes,
        "numeric_value_loaded_count": indicator_card["numeric_value_loaded_count"],
    }


def _role_source_rule_provenance_complete(role: dict[str, Any]) -> bool:
    return all(
        bool(role[field])
        for field in (
            "source_detail",
            "release_timing_detail",
            "freshness_detail",
            "transformation_detail",
            "rule_or_usability_detail",
            "provenance_detail",
            "data_mode_detail",
            "abstention_reason_detail",
        )
    )


def _present_count(rows: list[dict[str, Any]], field: str) -> int:
    return sum(bool(row[field]) for row in rows)


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        artifact.get(key) == value
        for key, value in expected.items()
        if key != "indicator_dashboard_explanation_drilldown_ready"
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
    contract = payload["indicator_dashboard_explanation_drilldown"]
    if not isinstance(contract, dict):
        raise ValueError("Phase62 drill-down contract must be a mapping")
    return contract
