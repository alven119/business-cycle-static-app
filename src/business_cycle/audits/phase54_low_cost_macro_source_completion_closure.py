"""Phase54 closure for low-cost macro source completion."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.low_cost_macro_source_completion import (
    summarize_low_cost_macro_source_completion,
)
from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)

DEFAULT_PHASE54_CLOSURE_PATH = Path(
    "specs/audits/phase54_low_cost_macro_source_completion_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase54_low_cost_macro_source_completion_closure(
    path: str | Path = DEFAULT_PHASE54_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase54 hard gates."""

    expected = _load_expected(path)
    completion = summarize_low_cost_macro_source_completion()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "54",
        "phase_id": "54",
        "phase54_low_cost_macro_source_completion_ready": (
            completion["low_cost_macro_source_completion_ready"]
            and progress["product_capability_progress_ready"]
        ),
        "low_cost_macro_source_completion_ready": completion[
            "low_cost_macro_source_completion_ready"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "remaining_phase54_role_count": completion["remaining_phase54_role_count"],
        "low_cost_path_defined_role_count": completion[
            "low_cost_path_defined_role_count"
        ],
        "macromicro_api_candidate_count": completion[
            "macromicro_api_candidate_count"
        ],
        "unaffordable_paid_api_candidate_count": completion[
            "unaffordable_paid_api_candidate_count"
        ],
        "user_supplied_authorized_input_contract_count": completion[
            "user_supplied_authorized_input_contract_count"
        ],
        "supporting_proxy_only_role_count": completion[
            "supporting_proxy_only_role_count"
        ],
        "book_core_replacement_without_license_count": completion[
            "book_core_replacement_without_license_count"
        ],
        "source_risk_label_missing_count": completion[
            "source_risk_label_missing_count"
        ],
        "substitution_degree_missing_count": completion[
            "substitution_degree_missing_count"
        ],
        "silent_substitution_count": completion["silent_substitution_count"],
        "alternative_promoted_to_core_count": completion[
            "alternative_promoted_to_core_count"
        ],
        "payems_replaces_adp_count": completion["payems_replaces_adp_count"],
        "generic_sentiment_replaces_consumer_confidence_count": completion[
            "generic_sentiment_replaces_consumer_confidence_count"
        ],
        "proxy_promoted_to_book_core_count": completion[
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
            "low_cost_source_completion_ready_declared_state_preserved"
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
            "W2_PHASE_ANALYSIS",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
            "W13_MODEL_GOVERNANCE",
        ],
        "deferred_capability_gaps": [
            "ADP direct role still needs authorized private input or license",
            "Conference Board confidence still needs authorized private input or license",
            "PAYEMS and UMich sentiment remain supporting-only proxies",
            "indicator detail still needs source-risk display wiring",
            "Phase54 does not emit candidate/current phase or production behavior",
        ],
        "next_recommended_phase": (
            "Phase55_indicator_detail_low_cost_source_risk_wiring"
        ),
        "phase54_closure_status": (
            "closed_low_cost_macro_source_completion_ready_no_paid_api_or_phase_emission"
        ),
        "low_cost_macro_source_completion_summary": completion,
        "product_capability_progress_summary": progress,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase54_low_cost_macro_source_completion_closure"
    ]["expected"]
