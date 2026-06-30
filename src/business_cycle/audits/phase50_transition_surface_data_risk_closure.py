"""Phase50 closure for transition-surface data-risk presentation."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase49_boom_transition_dashboard_closure import (
    summarize_phase49_boom_transition_dashboard_closure,
)

DEFAULT_PHASE50_CLOSURE_PATH = Path(
    "specs/audits/phase50_transition_surface_data_risk_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase50_transition_surface_data_risk_closure(
    path: str | Path = DEFAULT_PHASE50_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase50 hard gates."""

    expected = _load_expected(path)
    phase49 = summarize_phase49_boom_transition_dashboard_closure()
    summary: dict[str, Any] = {
        "phase": "50",
        "phase_id": "50",
        "phase50_transition_surface_data_risk_ready": (
            phase49["data_risk_surface_ready"]
            and phase49["silent_substitution_count"] == 0
            and phase49["alternative_promoted_to_core_count"] == 0
        ),
        **{
            key: phase49[key]
            for key in (
                "boom_transition_dashboard_surface_ready",
                "declared_current_phase",
                "legal_next_phase",
                "indicator_card_count",
                "data_risk_label_present_count",
                "source_credibility_label_present_count",
                "alternative_source_candidate_card_count",
                "substitution_degree_visible_count",
                "silent_substitution_count",
                "alternative_promoted_to_core_count",
                "data_risk_surface_ready",
                "browser_verification_ready",
                "browser_missing_required_element_count",
                "prohibited_claim_count",
                "prohibited_action_field_count",
                "standalone_classifier_added_count",
                "phase_rank_or_score_added_count",
                "selected_phase_output_count",
                "current_data_used_to_infer_declared_phase_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "declared_registry_modified",
                "production_behavior_change_count",
                "legacy_v1_behavior_modified_count",
                "portfolio_policy_output_count",
                "backtest_execution_count",
                "semantic_drift_count",
                "forbidden_repo_output_count",
                "raw_book_pdf_tracked_count",
                "tracked_data_raw_file_count",
                "product_doctrine_alignment_status",
                "legal_transition_semantics_preserved",
            )
        },
        "cycle_state_machine_alignment_status": "transition_surface_data_risk_ready",
        "portfolio_policy_research_alignment": "unchanged_no_policy_output",
        "historical_replay_backtest_alignment": "unchanged_no_replay_or_backtest",
        "deviation_cleanup_needed_count": 0,
        "north_star_alignment_status": "aligned",
        "web_surfaces_advanced": [
            "W1_OVERVIEW",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
        ],
        "product_capabilities_advanced": [
            "C2_TRANSITION_RISK_DETECTION",
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C6_SAFE_OUTPUT_GOVERNANCE",
        ],
        "deferred_capability_gaps": [
            "declared boom start date governance deferred to next phase",
            "alternative source candidates remain display risk guidance until wired",
            "production Pages dashboard remains legacy v1 until migration gate",
        ],
        "next_recommended_phase": "Phase51_declared_boom_start_date_governance",
        "phase50_closure_status": (
            "closed_transition_surface_data_risk_visible_no_substitution_promotion"
        ),
        "phase49_summary": phase49,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase50_transition_surface_data_risk_closure"
    ]["expected"]
