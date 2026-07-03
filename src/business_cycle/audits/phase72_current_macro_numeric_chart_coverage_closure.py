"""Phase72 current macro numeric/chart coverage closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.current_macro_numeric_chart_coverage import (
    summarize_current_macro_numeric_chart_coverage,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase72_current_macro_numeric_chart_coverage_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase72_current_macro_numeric_chart_coverage_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase72 hard gates."""

    expected = _load_expected(path)
    coverage = summarize_current_macro_numeric_chart_coverage()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "72",
        "phase_id": 72,
        "phase_label": "current_macro_numeric_chart_coverage_expansion",
        "current_macro_numeric_chart_coverage_ready": coverage[
            "current_macro_numeric_chart_coverage_ready"
        ],
        "role_count": coverage["role_count"],
        "role_with_official_series_count": coverage[
            "role_with_official_series_count"
        ],
        "role_without_official_series_count": coverage[
            "role_without_official_series_count"
        ],
        "unique_official_series_count": coverage["unique_official_series_count"],
        "fixture_seeded_series_count": coverage["fixture_seeded_series_count"],
        "role_with_numeric_context_count": coverage[
            "role_with_numeric_context_count"
        ],
        "role_with_chart_payload_count": coverage["role_with_chart_payload_count"],
        "role_with_available_chart_payload_count": coverage[
            "role_with_available_chart_payload_count"
        ],
        "role_with_ytd_available_chart_count": coverage[
            "role_with_ytd_available_chart_count"
        ],
        "role_with_trailing_1y_available_chart_count": coverage[
            "role_with_trailing_1y_available_chart_count"
        ],
        "role_with_trailing_5y_available_chart_count": coverage[
            "role_with_trailing_5y_available_chart_count"
        ],
        "chart_unavailable_role_count": coverage["chart_unavailable_role_count"],
        "chart_unavailable_policy_count": coverage[
            "chart_unavailable_policy_count"
        ],
        "chart_point_count": coverage["chart_point_count"],
        "latest_numeric_point_count": coverage["latest_numeric_point_count"],
        "role_with_source_risk_label_count": coverage[
            "role_with_source_risk_label_count"
        ],
        "fixture_cache_written_under_tmp": coverage[
            "fixture_cache_written_under_tmp"
        ],
        "repo_output_written_count": coverage["repo_output_written_count"],
        "fixture_mislabeled_as_live_count": coverage[
            "fixture_mislabeled_as_live_count"
        ],
        "point_in_time_claim_count": coverage["point_in_time_claim_count"],
        "numeric_context_promoted_to_phase_support_count": coverage[
            "numeric_context_promoted_to_phase_support_count"
        ],
        "missing_value_treated_as_neutral_count": coverage[
            "missing_value_treated_as_neutral_count"
        ],
        "unavailable_chart_treated_as_zero_count": coverage[
            "unavailable_chart_treated_as_zero_count"
        ],
        "prohibited_output_field_count": coverage["prohibited_output_field_count"],
        "current_data_used_to_infer_declared_phase_count": coverage[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": coverage[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": coverage[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": coverage["role_count_voting_added_count"],
        "candidate_phase_emitted": coverage["candidate_phase_emitted"],
        "current_phase_emitted": coverage["current_phase_emitted"],
        "production_behavior_change_count": coverage[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": coverage["semantic_drift_count"],
        "product_doctrine_alignment_status": coverage[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": coverage[
            "cycle_state_machine_alignment_status"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "phase72_closure_status": (
            "closed_current_macro_numeric_chart_coverage_expanded_"
            "declared_state_preserved"
        ),
    }
    summary["phase72_current_macro_numeric_chart_coverage_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["phase72_current_macro_numeric_chart_coverage_ready"]
        else "blocked"
    )
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase72_current_macro_numeric_chart_coverage_closure"][
            "hard_gates"
        ],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "phase72_current_macro_numeric_chart_coverage_ready"
    )
