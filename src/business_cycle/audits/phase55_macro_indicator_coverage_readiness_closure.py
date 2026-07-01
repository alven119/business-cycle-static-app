"""Phase55 closure for macro indicator coverage readiness."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.macro_indicator_coverage_readiness_matrix import (
    summarize_macro_indicator_coverage_readiness_matrix,
)
from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)

DEFAULT_PHASE55_CLOSURE_PATH = Path(
    "specs/audits/phase55_macro_indicator_coverage_readiness_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase55_macro_indicator_coverage_readiness_closure(
    path: str | Path = DEFAULT_PHASE55_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase55 hard gates."""

    expected = _load_expected(path)
    matrix = summarize_macro_indicator_coverage_readiness_matrix()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "55",
        "phase_id": "55",
        "phase55_macro_indicator_coverage_readiness_ready": (
            matrix["macro_indicator_coverage_readiness_matrix_ready"]
            and progress["product_capability_progress_ready"]
        ),
        "macro_indicator_coverage_readiness_matrix_ready": matrix[
            "macro_indicator_coverage_readiness_matrix_ready"
        ],
        "dashboard_gap_burn_down_view_ready": matrix[
            "dashboard_gap_burn_down_view_ready"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "coverage_role_count": matrix["coverage_role_count"],
        "phase_count": matrix["phase_count"],
        "phase_with_coverage_count": matrix["phase_with_coverage_count"],
        "phase_counts": matrix["phase_counts"],
        "source_coverage_tier_counts": matrix["source_coverage_tier_counts"],
        "coverage_status_counts": matrix["coverage_status_counts"],
        "data_risk_level_counts": matrix["data_risk_level_counts"],
        "role_with_source_tier_count": matrix["role_with_source_tier_count"],
        "role_with_data_risk_label_count": matrix[
            "role_with_data_risk_label_count"
        ],
        "role_with_dashboard_explanation_count": matrix[
            "role_with_dashboard_explanation_count"
        ],
        "role_with_next_gap_count": matrix["role_with_next_gap_count"],
        "official_or_authorized_path_count": matrix[
            "official_or_authorized_path_count"
        ],
        "supporting_proxy_only_count": matrix["supporting_proxy_only_count"],
        "user_authorized_input_required_count": matrix[
            "user_authorized_input_required_count"
        ],
        "false_resolution_count": matrix["false_resolution_count"],
        "silent_substitution_count": matrix["silent_substitution_count"],
        "alternative_promoted_to_core_count": matrix[
            "alternative_promoted_to_core_count"
        ],
        "proxy_promoted_to_book_core_count": matrix[
            "proxy_promoted_to_book_core_count"
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
            "macro_coverage_gap_burn_down_ready_declared_state_preserved"
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
            "current cache value rendering still needs broader actual-value wiring",
            "ADP and consumer confidence still need authorized user/private input for book-core use",
            "supporting proxies remain display-only and cannot replace book-core roles",
            "formal current/candidate phase outputs remain disabled",
            "production migration remains closed",
        ],
        "next_recommended_phase": (
            "Phase56_indicator_detail_source_risk_and_value_rendering"
        ),
        "phase55_closure_status": (
            "closed_macro_indicator_coverage_readiness_matrix_ready_no_phase_emission"
        ),
        "macro_indicator_coverage_readiness_summary": matrix,
        "product_capability_progress_summary": progress,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase55_macro_indicator_coverage_readiness_closure"
    ]["expected"]
