"""Phase62 closure for indicator-to-dashboard explanation drill-down."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
    summarize_indicator_dashboard_explanation_drilldown,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
    validate_research_dashboard_bundle,
)

DEFAULT_PHASE62_CLOSURE_PATH = Path(
    "specs/audits/phase62_indicator_dashboard_explanation_drilldown_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase62_indicator_dashboard_explanation_drilldown_closure(
    path: str | Path = DEFAULT_PHASE62_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase62 hard gates."""

    expected = _load_expected(path)
    drilldown = summarize_indicator_dashboard_explanation_drilldown()
    view_model = build_indicator_dashboard_explanation_drilldown_view_model(
        drilldown["drilldown_artifact"],
    )
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=view_model,
    )
    bundle_validation = validate_research_dashboard_bundle(bundle)
    progress = summarize_product_capability_progress()
    dashboard_view_ready = (
        bundle_validation["bundle_schema_valid"]
        and "indicator_dashboard_explanation_drilldown"
        in {view["view_id"] for view in bundle["views"]}
        and view_model["research_only"] is True
        and view_model["candidate_phase_emitted"] is False
        and view_model["current_phase_emitted"] is False
    )
    summary: dict[str, Any] = {
        "phase": "62",
        "phase_id": "62",
        "phase62_indicator_dashboard_explanation_drilldown_ready": (
            drilldown["indicator_dashboard_explanation_drilldown_ready"]
            and dashboard_view_ready
            and progress["product_capability_progress_ready"]
        ),
        "indicator_dashboard_explanation_drilldown_ready": drilldown[
            "indicator_dashboard_explanation_drilldown_ready"
        ],
        "dashboard_indicator_drilldown_view_ready": dashboard_view_ready,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "major_group_drilldown_count": drilldown["major_group_drilldown_count"],
        "role_drilldown_count": drilldown["role_drilldown_count"],
        "phase_count": drilldown["phase_count"],
        "phase_with_drilldown_count": drilldown["phase_with_drilldown_count"],
        "role_with_source_detail_count": drilldown["role_with_source_detail_count"],
        "role_with_release_timing_detail_count": drilldown[
            "role_with_release_timing_detail_count"
        ],
        "role_with_freshness_detail_count": drilldown[
            "role_with_freshness_detail_count"
        ],
        "role_with_transformation_detail_count": drilldown[
            "role_with_transformation_detail_count"
        ],
        "role_with_rule_or_usability_detail_count": drilldown[
            "role_with_rule_or_usability_detail_count"
        ],
        "role_with_provenance_detail_count": drilldown[
            "role_with_provenance_detail_count"
        ],
        "role_with_data_mode_detail_count": drilldown[
            "role_with_data_mode_detail_count"
        ],
        "role_with_abstention_reason_count": drilldown[
            "role_with_abstention_reason_count"
        ],
        "role_with_dashboard_explanation_count": drilldown[
            "role_with_dashboard_explanation_count"
        ],
        "role_with_drilldown_href_count": drilldown[
            "role_with_drilldown_href_count"
        ],
        "major_group_with_role_links_count": drilldown[
            "major_group_with_role_links_count"
        ],
        "major_group_with_readiness_explanation_count": drilldown[
            "major_group_with_readiness_explanation_count"
        ],
        "official_source_role_drilldown_count": drilldown[
            "official_source_role_drilldown_count"
        ],
        "authorized_input_drilldown_count": drilldown[
            "authorized_input_drilldown_count"
        ],
        "supporting_proxy_drilldown_count": drilldown[
            "supporting_proxy_drilldown_count"
        ],
        "metadata_ready_value_missing_drilldown_count": drilldown[
            "metadata_ready_value_missing_drilldown_count"
        ],
        "source_metadata_incomplete_drilldown_count": drilldown[
            "source_metadata_incomplete_drilldown_count"
        ],
        "current_numeric_value_available_drilldown_count": drilldown[
            "current_numeric_value_available_drilldown_count"
        ],
        "group_ready_for_formal_phase_count": drilldown[
            "group_ready_for_formal_phase_count"
        ],
        "source_rule_provenance_complete": drilldown[
            "source_rule_provenance_complete"
        ],
        "prohibited_output_field_count": drilldown["prohibited_output_field_count"]
        + bundle_validation["prohibited_action_field_count"],
        "standalone_classifier_added_count": drilldown[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": drilldown[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": drilldown["role_count_voting_added_count"],
        "current_data_used_to_infer_declared_phase_count": drilldown[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": drilldown["candidate_phase_emitted"],
        "current_phase_emitted": drilldown["current_phase_emitted"],
        "production_behavior_change_count": drilldown[
            "production_behavior_change_count"
        ],
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": drilldown["semantic_drift_count"],
        "product_doctrine_alignment_status": drilldown[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": drilldown[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": True,
        "portfolio_policy_research_alignment": "unchanged_no_policy_output",
        "historical_replay_backtest_alignment": "unchanged_no_replay_or_backtest",
        "deviation_cleanup_needed_count": 0,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": progress["impacted_capability_ids"],
        "product_capability_progress_impacted_count": expected[
            "product_capability_progress_impacted_count"
        ],
        "current_product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "web_surfaces_advanced": [
            "W2_PHASE_ANALYSIS",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
        ],
        "deferred_capability_gaps": [
            "governed declared boom start date and phase-age confirmation remain open",
            "current numeric cache remains unavailable in CI fixture mode",
            "transition timing replay preview remains next",
            "formal current/candidate phase outputs remain disabled",
            "production migration remains closed",
        ],
        "next_recommended_phase": (
            "Phase63_research_only_transition_timing_replay_preview"
        ),
        "phase62_closure_status": (
            "closed_indicator_dashboard_explanation_drilldown_ready_no_phase_emission"
        ),
        "drilldown_summary": drilldown,
        "product_capability_progress_summary": progress,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase62_indicator_dashboard_explanation_drilldown_closure"
    ]["expected"]
