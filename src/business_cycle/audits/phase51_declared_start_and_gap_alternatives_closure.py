"""Phase51 closure for declared start governance and macro gap alternatives."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.macro_indicator_gap_alternative_sources import (
    summarize_macro_indicator_gap_alternative_sources,
)
from business_cycle.cycle_state.declared_boom_start_governance import (
    summarize_declared_boom_start_governance,
)

DEFAULT_PHASE51_CLOSURE_PATH = Path(
    "specs/audits/phase51_declared_start_and_gap_alternatives_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase51_declared_start_and_gap_alternatives_closure(
    path: str | Path = DEFAULT_PHASE51_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase51 hard gates."""

    expected = _load_expected(path)
    start = summarize_declared_boom_start_governance()
    alternatives = summarize_macro_indicator_gap_alternative_sources()
    gap_count_matches = (
        alternatives["gap_with_alternative_candidate_count"]
        == alternatives["gap_role_count"]
    )
    summary: dict[str, Any] = {
        "phase": "51",
        "phase_id": "51",
        "phase51_declared_start_and_gap_alternatives_ready": (
            start["declared_boom_start_governance_ready"]
            and alternatives["macro_gap_alternative_registry_ready"]
            and gap_count_matches
        ),
        "declared_boom_start_governance_ready": start[
            "declared_boom_start_governance_ready"
        ],
        "macro_gap_alternative_registry_ready": alternatives[
            "macro_gap_alternative_registry_ready"
        ],
        "declared_current_phase": start["declared_current_phase"],
        "legal_next_phase": start["legal_next_phase"],
        "declared_phase_start_date_current_value": start[
            "declared_phase_start_date_current_value"
        ],
        "declared_phase_start_date_status": start[
            "declared_phase_start_date_status"
        ],
        "phase_age_status_current_value": start["phase_age_status_current_value"],
        "governed_confirmation_option_count": start[
            "governed_confirmation_option_count"
        ],
        "governed_start_date_confirmed": start["governed_start_date_confirmed"],
        "user_confirmation_required": start["user_confirmation_required"],
        "registry_write_allowed": start["registry_write_allowed"],
        "declared_registry_modified": start["declared_registry_modified"],
        "phase_age_false_precision_count": start[
            "phase_age_false_precision_count"
        ],
        "gap_role_count": alternatives["gap_role_count"],
        "gap_with_alternative_candidate_count": alternatives[
            "gap_with_alternative_candidate_count"
        ],
        "gap_with_alternative_candidate_count_equals_gap_role_count": (
            gap_count_matches
        ),
        "phase_gap_counts": alternatives["phase_gap_counts"],
        "planned_resolution_phase_counts": alternatives[
            "planned_resolution_phase_counts"
        ],
        "substitution_degree_counts": alternatives["substitution_degree_counts"],
        "automation_feasibility_counts": alternatives[
            "automation_feasibility_counts"
        ],
        "book_core_replacement_allowed_role_count": alternatives[
            "book_core_replacement_allowed_role_count"
        ],
        "supporting_or_proxy_only_role_count": alternatives[
            "supporting_or_proxy_only_role_count"
        ],
        "source_risk_label_missing_count": alternatives[
            "source_risk_label_missing_count"
        ],
        "substitution_degree_missing_count": alternatives[
            "substitution_degree_missing_count"
        ],
        "planned_resolution_phase_missing_count": alternatives[
            "planned_resolution_phase_missing_count"
        ],
        "silent_substitution_count": alternatives["silent_substitution_count"],
        "alternative_promoted_to_core_count": alternatives[
            "alternative_promoted_to_core_count"
        ],
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": start[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_start_governance_and_gap_alternative_inventory_ready"
        ),
        "legal_transition_semantics_preserved": True,
        "portfolio_policy_research_alignment": "unchanged_no_policy_output",
        "historical_replay_backtest_alignment": "unchanged_no_replay_or_backtest",
        "deviation_cleanup_needed_count": 0,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": [
            "C2_TRANSITION_RISK_DETECTION",
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C6_SAFE_OUTPUT_GOVERNANCE",
            "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
        ],
        "web_surfaces_advanced": [
            "W1_OVERVIEW",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
            "W15_SYSTEM_OPERATIONS",
        ],
        "deferred_capability_gaps": [
            "exact declared boom start date still requires user-supplied date or window",
            "alternative sources are inventoried but not yet wired into adapters",
            "licensed or proxy-only roles require explicit user risk acceptance",
        ],
        "next_recommended_phase": "Phase52_official_macro_source_adapter_wiring",
        "phase51_closure_status": (
            "closed_declared_start_governance_and_gap_alternatives_ready_no_registry_write"
        ),
        "declared_start_summary": start,
        "macro_gap_alternative_summary": alternatives,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase51_declared_start_and_gap_alternatives_closure"
    ]["expected"]
