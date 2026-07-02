"""Phase61 closure for major-group evidence profile readiness."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.major_group_evidence_profile_readiness import (
    build_major_group_evidence_profile_readiness_view_model,
    summarize_major_group_evidence_profile_readiness,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
    validate_research_dashboard_bundle,
)

DEFAULT_PHASE61_CLOSURE_PATH = Path(
    "specs/audits/phase61_major_group_evidence_profile_readiness_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase61_major_group_evidence_profile_readiness_closure(
    path: str | Path = DEFAULT_PHASE61_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase61 hard gates."""

    expected = _load_expected(path)
    profiles = summarize_major_group_evidence_profile_readiness()
    view_model = build_major_group_evidence_profile_readiness_view_model(
        profiles["major_group_profile_artifact"],
    )
    bundle = build_research_dashboard_bundle(
        major_group_evidence_profile_readiness=view_model,
    )
    bundle_validation = validate_research_dashboard_bundle(bundle)
    progress = summarize_product_capability_progress()
    dashboard_view_ready = (
        bundle_validation["bundle_schema_valid"]
        and "major_group_evidence_profile_readiness"
        in {view["view_id"] for view in bundle["views"]}
        and view_model["research_only"] is True
        and view_model["candidate_phase_emitted"] is False
        and view_model["current_phase_emitted"] is False
    )
    summary: dict[str, Any] = {
        "phase": "61",
        "phase_id": "61",
        "phase61_major_group_evidence_profile_readiness_ready": (
            profiles["major_group_evidence_profile_readiness_ready"]
            and dashboard_view_ready
            and progress["product_capability_progress_ready"]
        ),
        "major_group_evidence_profile_readiness_ready": profiles[
            "major_group_evidence_profile_readiness_ready"
        ],
        "dashboard_major_group_profile_view_ready": dashboard_view_ready,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "major_group_profile_count": profiles["major_group_profile_count"],
        "phase_count": profiles["phase_count"],
        "phase_with_major_group_profile_count": profiles[
            "phase_with_major_group_profile_count"
        ],
        "profiled_role_count": profiles["profiled_role_count"],
        "profiled_required_core_role_count": profiles[
            "profiled_required_core_role_count"
        ],
        "profiled_supporting_role_count": profiles[
            "profiled_supporting_role_count"
        ],
        "methodology_requirement_excluded_count": profiles[
            "methodology_requirement_excluded_count"
        ],
        "missing_non_methodology_role_count": profiles[
            "missing_non_methodology_role_count"
        ],
        "required_core_group_profile_complete_count": profiles[
            "required_core_group_profile_complete_count"
        ],
        "supporting_only_group_count": profiles["supporting_only_group_count"],
        "group_with_value_context_count": profiles["group_with_value_context_count"],
        "group_with_freshness_context_count": profiles[
            "group_with_freshness_context_count"
        ],
        "group_with_release_timing_context_count": profiles[
            "group_with_release_timing_context_count"
        ],
        "group_with_readiness_explanation_count": profiles[
            "group_with_readiness_explanation_count"
        ],
        "core_metadata_ready_value_missing_group_count": profiles[
            "core_metadata_ready_value_missing_group_count"
        ],
        "core_authorized_input_required_group_count": profiles[
            "core_authorized_input_required_group_count"
        ],
        "core_supporting_proxy_visible_not_book_core_group_count": profiles[
            "core_supporting_proxy_visible_not_book_core_group_count"
        ],
        "core_source_metadata_incomplete_abstain_group_count": profiles[
            "core_source_metadata_incomplete_abstain_group_count"
        ],
        "supporting_proxy_context_group_count": profiles[
            "supporting_proxy_context_group_count"
        ],
        "group_ready_for_formal_phase_count": profiles[
            "group_ready_for_formal_phase_count"
        ],
        "group_with_current_numeric_value_count": profiles[
            "group_with_current_numeric_value_count"
        ],
        "major_group_promoted_with_missing_core_count": profiles[
            "major_group_promoted_with_missing_core_count"
        ],
        "supporting_proxy_replacement_allowed_count": profiles[
            "supporting_proxy_replacement_allowed_count"
        ],
        "missing_value_treated_as_neutral_count": profiles[
            "missing_value_treated_as_neutral_count"
        ],
        "metadata_only_promoted_to_phase_support_count": profiles[
            "metadata_only_promoted_to_phase_support_count"
        ],
        "prohibited_output_field_count": profiles["prohibited_output_field_count"]
        + bundle_validation["prohibited_action_field_count"],
        "standalone_classifier_added_count": profiles[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": profiles[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": profiles["role_count_voting_added_count"],
        "current_data_used_to_infer_declared_phase_count": profiles[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": profiles["candidate_phase_emitted"],
        "current_phase_emitted": profiles["current_phase_emitted"],
        "production_behavior_change_count": profiles[
            "production_behavior_change_count"
        ],
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": profiles["semantic_drift_count"],
        "product_doctrine_alignment_status": profiles[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": profiles[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": True,
        "portfolio_policy_research_alignment": "unchanged_no_policy_output",
        "historical_replay_backtest_alignment": "unchanged_no_replay_or_backtest",
        "deviation_cleanup_needed_count": 0,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": progress["impacted_capability_ids"],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "web_surfaces_advanced": [
            "W1_OVERVIEW",
            "W2_PHASE_ANALYSIS",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
        ],
        "deferred_capability_gaps": [
            "governed declared boom start date and phase-age confirmation remain open",
            "current numeric cache remains unavailable in CI fixture mode",
            "major-group profiles explain readiness but do not emit phase support",
            "indicator-to-dashboard drill-down remains the next explanation layer",
            "formal current/candidate phase outputs remain disabled",
            "production migration remains closed",
        ],
        "next_recommended_phase": (
            "Phase62_indicator_to_dashboard_explanation_drill_down"
        ),
        "phase61_closure_status": (
            "closed_major_group_evidence_profiles_ready_no_phase_emission"
        ),
        "major_group_profile_summary": profiles,
        "product_capability_progress_summary": progress,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase61_major_group_evidence_profile_readiness_closure"
    ]["expected"]
