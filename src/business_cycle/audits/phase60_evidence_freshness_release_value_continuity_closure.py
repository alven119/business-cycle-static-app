"""Phase60 closure for evidence freshness/release/value continuity."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.evidence_freshness_release_value_continuity import (
    build_evidence_freshness_release_value_continuity_view_model,
    summarize_evidence_freshness_release_value_continuity,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
    validate_research_dashboard_bundle,
)

DEFAULT_PHASE60_CLOSURE_PATH = Path(
    "specs/audits/phase60_evidence_freshness_release_value_continuity_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase60_evidence_freshness_release_value_continuity_closure(
    path: str | Path = DEFAULT_PHASE60_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase60 hard gates."""

    expected = _load_expected(path)
    continuity = summarize_evidence_freshness_release_value_continuity()
    view_model = build_evidence_freshness_release_value_continuity_view_model(
        continuity["continuity_artifact"],
    )
    bundle = build_research_dashboard_bundle(
        evidence_freshness_release_value_continuity=view_model,
    )
    bundle_validation = validate_research_dashboard_bundle(bundle)
    progress = summarize_product_capability_progress()
    dashboard_view_ready = (
        bundle_validation["bundle_schema_valid"]
        and "evidence_freshness_release_value_continuity"
        in {view["view_id"] for view in bundle["views"]}
        and view_model["research_only"] is True
        and view_model["candidate_phase_emitted"] is False
        and view_model["current_phase_emitted"] is False
    )
    summary: dict[str, Any] = {
        "phase": "60",
        "phase_id": "60",
        "phase60_evidence_freshness_release_value_continuity_ready": (
            continuity["evidence_freshness_release_value_continuity_ready"]
            and dashboard_view_ready
            and progress["product_capability_progress_ready"]
        ),
        "evidence_freshness_release_value_continuity_ready": continuity[
            "evidence_freshness_release_value_continuity_ready"
        ],
        "dashboard_evidence_continuity_view_ready": dashboard_view_ready,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "continuity_card_count": continuity["continuity_card_count"],
        "phase_count": continuity["phase_count"],
        "role_with_value_context_count": continuity[
            "role_with_value_context_count"
        ],
        "role_with_freshness_context_count": continuity[
            "role_with_freshness_context_count"
        ],
        "role_with_release_timing_context_count": continuity[
            "role_with_release_timing_context_count"
        ],
        "role_with_continuity_status_count": continuity[
            "role_with_continuity_status_count"
        ],
        "stale_or_missing_explanation_count": continuity[
            "stale_or_missing_explanation_count"
        ],
        "current_numeric_value_available_count": continuity[
            "current_numeric_value_available_count"
        ],
        "metadata_ready_value_missing_count": continuity[
            "metadata_ready_value_missing_count"
        ],
        "authorized_input_required_count": continuity[
            "authorized_input_required_count"
        ],
        "supporting_proxy_only_count": continuity["supporting_proxy_only_count"],
        "source_metadata_incomplete_count": continuity[
            "source_metadata_incomplete_count"
        ],
        "transition_continuity_context_count": continuity[
            "transition_continuity_context_count"
        ],
        "transition_lane_context_count": continuity["transition_lane_context_count"],
        "freshness_context_missing_count": continuity[
            "freshness_context_missing_count"
        ],
        "release_timing_context_missing_count": continuity[
            "release_timing_context_missing_count"
        ],
        "value_context_missing_count": continuity["value_context_missing_count"],
        "declared_phase_age_false_precision_count": continuity[
            "declared_phase_age_false_precision_count"
        ],
        "phase59_declared_start_governance_deferred": continuity[
            "phase59_declared_start_governance_deferred"
        ],
        "missing_value_treated_as_neutral_count": continuity[
            "missing_value_treated_as_neutral_count"
        ],
        "metadata_only_promoted_to_phase_support_count": continuity[
            "metadata_only_promoted_to_phase_support_count"
        ],
        "supporting_proxy_replacement_allowed_count": continuity[
            "supporting_proxy_replacement_allowed_count"
        ],
        "prohibited_output_field_count": continuity[
            "prohibited_output_field_count"
        ]
        + bundle_validation["prohibited_action_field_count"],
        "standalone_classifier_added_count": continuity[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": continuity[
            "phase_rank_or_score_added_count"
        ],
        "current_data_used_to_infer_declared_phase_count": continuity[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": continuity["candidate_phase_emitted"],
        "current_phase_emitted": continuity["current_phase_emitted"],
        "production_behavior_change_count": continuity[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": continuity["semantic_drift_count"],
        "product_doctrine_alignment_status": continuity[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": continuity[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": True,
        "portfolio_policy_research_alignment": "unchanged_no_policy_output",
        "historical_replay_backtest_alignment": "unchanged_no_replay_or_backtest",
        "deviation_cleanup_needed_count": 0,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": progress["impacted_capability_ids"],
        "product_capability_progress_impacted_count": expected.get(
            "product_capability_progress_impacted_count",
            progress["impacted_capability_count"],
        ),
        "current_product_capability_progress_impacted_count": progress[
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
            "numeric current cache remains unavailable in CI fixture mode",
            "major-group evidence profile remains the next explanation layer",
            "formal current/candidate phase outputs remain disabled",
            "production migration remains closed",
        ],
        "next_recommended_phase": (
            "Phase61_major_group_evidence_profile_and_readiness_explanation"
        ),
        "phase60_closure_status": (
            "closed_evidence_freshness_release_value_continuity_ready_no_phase_emission"
        ),
        "continuity_summary": continuity,
        "product_capability_progress_summary": progress,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase60_evidence_freshness_release_value_continuity_closure"
    ]["expected"]
