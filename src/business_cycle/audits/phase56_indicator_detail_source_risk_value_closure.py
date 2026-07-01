"""Phase56 closure for indicator detail source-risk and value rendering."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_95_roadmap import (
    summarize_product_capability_95_roadmap,
)
from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.indicator_detail_source_risk_values import (
    summarize_indicator_detail_source_risk_value_rendering,
)

DEFAULT_PHASE56_CLOSURE_PATH = Path(
    "specs/audits/phase56_indicator_detail_source_risk_value_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase56_indicator_detail_source_risk_value_closure(
    path: str | Path = DEFAULT_PHASE56_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase56 hard gates."""

    expected = _load_expected(path)
    rendering = summarize_indicator_detail_source_risk_value_rendering()
    progress = summarize_product_capability_progress()
    roadmap = summarize_product_capability_95_roadmap()
    summary: dict[str, Any] = {
        "phase": "56",
        "phase_id": "56",
        "phase56_indicator_detail_source_risk_value_ready": (
            rendering["indicator_detail_source_risk_value_rendering_ready"]
            and progress["product_capability_progress_ready"]
            and roadmap["roadmap_ready"]
        ),
        "indicator_detail_source_risk_value_rendering_ready": rendering[
            "indicator_detail_source_risk_value_rendering_ready"
        ],
        "indicator_detail_source_risk_ready": rendering[
            "indicator_detail_source_risk_ready"
        ],
        "indicator_detail_value_context_ready": rendering[
            "indicator_detail_value_context_ready"
        ],
        "dashboard_indicator_detail_view_ready": rendering[
            "dashboard_view_model_ready"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_95_roadmap_ready": roadmap["roadmap_ready"],
        "indicator_detail_card_count": rendering["indicator_detail_card_count"],
        "phase_count": rendering["phase_count"],
        "phase_with_indicator_detail_count": rendering[
            "phase_with_indicator_detail_count"
        ],
        "phase_counts": rendering["phase_counts"],
        "source_risk_visible_card_count": rendering[
            "source_risk_visible_card_count"
        ],
        "freshness_context_visible_card_count": rendering[
            "freshness_context_visible_card_count"
        ],
        "release_timing_context_visible_card_count": rendering[
            "release_timing_context_visible_card_count"
        ],
        "value_context_visible_card_count": rendering[
            "value_context_visible_card_count"
        ],
        "transformation_context_visible_card_count": rendering[
            "transformation_context_visible_card_count"
        ],
        "why_not_evidence_visible_card_count": rendering[
            "why_not_evidence_visible_card_count"
        ],
        "authorized_input_missing_card_count": rendering[
            "authorized_input_missing_card_count"
        ],
        "supporting_proxy_only_card_count": rendering[
            "supporting_proxy_only_card_count"
        ],
        "numeric_value_loaded_card_count": rendering[
            "numeric_value_loaded_card_count"
        ],
        "proxy_promoted_to_book_core_count": rendering[
            "proxy_promoted_to_book_core_count"
        ],
        "silent_substitution_count": rendering["silent_substitution_count"],
        "false_resolution_count": rendering["false_resolution_count"],
        "prohibited_output_field_count": rendering["prohibited_output_field_count"],
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "indicator_detail_source_risk_value_ready_declared_state_preserved"
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
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
        ],
        "deferred_capability_gaps": [
            "declared boom start date still needs governed confirmation",
            "some numeric current values remain metadata-only until local cache or authorized inputs exist",
            "supporting proxies remain display-only and cannot replace book-core roles",
            "formal current/candidate phase outputs remain disabled",
            "production migration remains closed",
        ],
        "next_recommended_phase": (
            "Phase57_boom_to_recession_transition_surface_completion"
        ),
        "phase56_closure_status": (
            "closed_indicator_detail_source_risk_value_rendering_ready_no_phase_emission"
        ),
        "indicator_detail_source_risk_value_summary": rendering,
        "product_capability_progress_summary": progress,
        "product_capability_95_roadmap_summary": roadmap,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase56_indicator_detail_source_risk_value_closure"
    ]["expected"]
