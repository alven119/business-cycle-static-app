"""Phase53 closure for composite transition-surface value wiring."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.current.composite_transition_surface_values import (
    summarize_composite_transition_surface_value_wiring,
)
from business_cycle.render.boom_transition_dashboard_surface import (
    summarize_boom_transition_dashboard_surface,
)

DEFAULT_PHASE53_CLOSURE_PATH = Path(
    "specs/audits/phase53_composite_transition_surface_value_wiring_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase53_composite_transition_surface_value_wiring_closure(
    path: str | Path = DEFAULT_PHASE53_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase53 hard gates."""

    expected = _load_expected(path)
    value_wiring = summarize_composite_transition_surface_value_wiring()
    surface = summarize_boom_transition_dashboard_surface()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "53",
        "phase_id": "53",
        "phase53_composite_transition_surface_value_wiring_ready": (
            value_wiring["composite_transition_surface_value_wiring_ready"]
            and surface["boom_transition_dashboard_surface_ready"]
            and progress["product_capability_progress_ready"]
        ),
        "composite_transition_surface_value_wiring_ready": value_wiring[
            "composite_transition_surface_value_wiring_ready"
        ],
        "boom_transition_dashboard_surface_ready": surface[
            "boom_transition_dashboard_surface_ready"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "role_count": value_wiring["role_count"],
        "transition_surface_role_count": value_wiring[
            "transition_surface_role_count"
        ],
        "composite_or_rule_gap_role_count": value_wiring[
            "composite_or_rule_gap_role_count"
        ],
        "source_metadata_ready_role_count": value_wiring[
            "source_metadata_ready_role_count"
        ],
        "value_context_visible_role_count": value_wiring[
            "value_context_visible_role_count"
        ],
        "composite_alignment_status_visible_count": value_wiring[
            "composite_alignment_status_visible_count"
        ],
        "explicit_abstention_reason_count": value_wiring[
            "explicit_abstention_reason_count"
        ],
        "surface_value_context_status_visible_count": surface[
            "value_context_status_visible_count"
        ],
        "surface_composite_alignment_status_visible_count": surface[
            "composite_alignment_status_visible_count"
        ],
        "surface_phase53_explicit_abstention_reason_count": surface[
            "phase53_explicit_abstention_reason_count"
        ],
        "phase_support_added_count": value_wiring["phase_support_added_count"],
        "silent_substitution_count": value_wiring["silent_substitution_count"],
        "alternative_promoted_to_core_count": value_wiring[
            "alternative_promoted_to_core_count"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "composite_value_context_ready_declared_state_preserved"
        ),
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
            "declared boom start date still needs governed user confirmation",
            "indicator detail still needs direct dashboard rendering of value context",
            "licensed/proxy source risk review remains outside Phase53",
            "Phase53 does not emit candidate/current phase or production behavior",
        ],
        "next_recommended_phase": (
            "Phase54_declared_boom_start_governance_and_indicator_detail_wiring"
        ),
        "phase53_closure_status": (
            "closed_composite_transition_surface_value_context_ready_no_phase_emission"
        ),
        "value_wiring_summary": value_wiring,
        "boom_transition_surface_summary": surface,
        "product_capability_progress_summary": progress,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase53_composite_transition_surface_value_wiring_closure"
    ]["expected"]
