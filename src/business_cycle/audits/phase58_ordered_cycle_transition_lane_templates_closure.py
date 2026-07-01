"""Phase58 closure for full ordered-cycle transition lane templates."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.ordered_cycle_transition_lane_templates import (
    build_full_ordered_cycle_transition_lane_template_view_model,
    summarize_full_ordered_cycle_transition_lane_templates,
)

DEFAULT_PHASE58_CLOSURE_PATH = Path(
    "specs/audits/phase58_ordered_cycle_transition_lane_templates_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase58_ordered_cycle_transition_lane_templates_closure(
    path: str | Path = DEFAULT_PHASE58_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase58 hard gates."""

    expected = _load_expected(path)
    templates = summarize_full_ordered_cycle_transition_lane_templates()
    view_model = build_full_ordered_cycle_transition_lane_template_view_model(
        templates["transition_lane_templates"],
    )
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "58",
        "phase_id": "58",
        "phase58_ordered_cycle_transition_lane_templates_ready": (
            templates["full_ordered_cycle_transition_lane_templates_ready"]
            and _view_model_ready(view_model)
            and progress["product_capability_progress_ready"]
        ),
        "full_ordered_cycle_transition_lane_templates_ready": templates[
            "full_ordered_cycle_transition_lane_templates_ready"
        ],
        "dashboard_ordered_cycle_transition_template_view_ready": _view_model_ready(
            view_model,
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "ordered_cycle_state_machine_ready": templates[
            "ordered_cycle_state_machine_ready"
        ],
        "legal_cycle_order_valid": templates["legal_cycle_order_valid"],
        "legal_transition_template_count": templates[
            "legal_transition_template_count"
        ],
        "legal_transition_template_with_state_machine_match_count": templates[
            "legal_transition_template_with_state_machine_match_count"
        ],
        "lane_template_count": templates["lane_template_count"],
        "continuation_lane_template_count": templates[
            "continuation_lane_template_count"
        ],
        "watch_lane_template_count": templates["watch_lane_template_count"],
        "confirmation_lane_template_count": templates[
            "confirmation_lane_template_count"
        ],
        "transition_with_continuation_lane_count": templates[
            "transition_with_continuation_lane_count"
        ],
        "transition_with_watch_lane_count": templates[
            "transition_with_watch_lane_count"
        ],
        "transition_with_confirmation_lane_count": templates[
            "transition_with_confirmation_lane_count"
        ],
        "watch_confirmation_separation_valid": templates[
            "watch_confirmation_separation_valid"
        ],
        "supporting_only_visible_count": templates[
            "supporting_only_visible_count"
        ],
        "supporting_only_role_replacement_allowed_count": templates[
            "supporting_only_role_replacement_allowed_count"
        ],
        "modern_extension_promoted_to_book_core_count": templates[
            "modern_extension_promoted_to_book_core_count"
        ],
        "proxy_promoted_to_book_core_count": templates[
            "proxy_promoted_to_book_core_count"
        ],
        "silent_substitution_count": templates["silent_substitution_count"],
        "phase_support_added_count": templates["phase_support_added_count"],
        "prohibited_output_field_count": templates["prohibited_output_field_count"],
        "standalone_classifier_added_count": templates[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": templates[
            "phase_rank_or_score_added_count"
        ],
        "current_data_used_to_infer_declared_phase_count": templates[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": templates["candidate_phase_emitted"],
        "current_phase_emitted": templates["current_phase_emitted"],
        "production_behavior_change_count": templates[
            "production_behavior_change_count"
        ],
        "legacy_v1_behavior_modified_count": templates[
            "legacy_v1_behavior_modified_count"
        ],
        "portfolio_policy_output_count": templates["portfolio_policy_output_count"],
        "backtest_execution_count": templates["backtest_execution_count"],
        "semantic_drift_count": templates["semantic_drift_count"],
        "product_doctrine_alignment_status": templates[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": templates[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": templates[
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
            "full ordered-cycle templates are research-only and not operational evidence",
            "declared boom start date still needs governed confirmation",
            "current numeric continuity and release freshness need Phase60 refinement",
            "major-group evidence profile remains a next explanation layer",
            "formal current/candidate phase outputs remain disabled",
            "production migration remains closed",
        ],
        "next_recommended_phase": (
            "Phase59_governed_declared_boom_start_and_phase_age_confirmation"
        ),
        "phase58_closure_status": (
            "closed_full_ordered_cycle_transition_lane_templates_ready_no_phase_emission"
        ),
        "transition_lane_template_summary": templates,
        "product_capability_progress_summary": progress,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _view_model_ready(view_model: dict[str, Any]) -> bool:
    return (
        view_model["view_id"] == "full_ordered_cycle_transition_lane_templates"
        and view_model["output_mode"]
        == "research_only_full_ordered_cycle_transition_lane_templates"
        and view_model["research_only"] is True
        and view_model["candidate_phase_emitted"] is False
        and view_model["current_phase_emitted"] is False
    )


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase58_ordered_cycle_transition_lane_templates_closure"
    ]["expected"]
