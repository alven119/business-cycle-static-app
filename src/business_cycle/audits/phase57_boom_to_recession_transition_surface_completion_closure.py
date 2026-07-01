"""Phase57 closure for boom-to-recession transition surface completion."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.boom_to_recession_transition_surface import (
    build_boom_to_recession_transition_surface_view_model,
    summarize_boom_to_recession_transition_surface_completion,
)

DEFAULT_PHASE57_CLOSURE_PATH = Path(
    "specs/audits/phase57_boom_to_recession_transition_surface_completion_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase57_boom_to_recession_transition_surface_completion_closure(
    path: str | Path = DEFAULT_PHASE57_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase57 hard gates."""

    expected = _load_expected(path)
    surface = summarize_boom_to_recession_transition_surface_completion()
    view_model = build_boom_to_recession_transition_surface_view_model(
        surface["transition_surface_completion"],
    )
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "57",
        "phase_id": "57",
        "phase57_boom_to_recession_transition_surface_completion_ready": (
            surface["boom_to_recession_transition_surface_completion_ready"]
            and _view_model_ready(view_model)
            and progress["product_capability_progress_ready"]
        ),
        "boom_to_recession_transition_surface_completion_ready": surface[
            "boom_to_recession_transition_surface_completion_ready"
        ],
        "dashboard_transition_surface_completion_view_ready": _view_model_ready(
            view_model,
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "declared_current_phase": surface["declared_current_phase"],
        "legal_next_phase": surface["legal_next_phase"],
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
            "declared boom start date still needs governed confirmation",
            "priority indicators remain research-only explanation context",
            "some current numeric values remain metadata-only until cache or authorized input exists",
            "formal current/candidate phase outputs remain disabled",
            "production migration remains closed",
        ],
        "next_recommended_phase": (
            "Phase58_full_ordered_cycle_transition_lane_templates"
        ),
        "phase57_closure_status": (
            "closed_boom_to_recession_transition_surface_completed_no_phase_emission"
        ),
        "transition_surface_completion_summary": surface,
        "product_capability_progress_summary": progress,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _view_model_ready(view_model: dict[str, Any]) -> bool:
    return (
        view_model["view_id"] == "boom_to_recession_transition_surface_completion"
        and view_model["output_mode"]
        == "research_only_boom_to_recession_transition_surface"
        and view_model["research_only"] is True
        and view_model["candidate_phase_emitted"] is False
        and view_model["current_phase_emitted"] is False
    )


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase57_boom_to_recession_transition_surface_completion_closure"
    ]["expected"]
