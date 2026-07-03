#!/usr/bin/env python
"""Show Phase72 current macro numeric/chart coverage closure."""

from __future__ import annotations

from business_cycle.audits.phase72_current_macro_numeric_chart_coverage_closure import (
    summarize_phase72_current_macro_numeric_chart_coverage_closure,
)


def main() -> int:
    summary = summarize_phase72_current_macro_numeric_chart_coverage_closure()
    keys = (
        "phase",
        "phase72_current_macro_numeric_chart_coverage_ready",
        "current_macro_numeric_chart_coverage_ready",
        "role_count",
        "role_with_official_series_count",
        "role_without_official_series_count",
        "unique_official_series_count",
        "fixture_seeded_series_count",
        "role_with_numeric_context_count",
        "role_with_available_chart_payload_count",
        "role_with_ytd_available_chart_count",
        "role_with_trailing_1y_available_chart_count",
        "role_with_trailing_5y_available_chart_count",
        "chart_unavailable_role_count",
        "chart_point_count",
        "fixture_cache_written_under_tmp",
        "repo_output_written_count",
        "fixture_mislabeled_as_live_count",
        "point_in_time_claim_count",
        "numeric_context_promoted_to_phase_support_count",
        "missing_value_treated_as_neutral_count",
        "unavailable_chart_treated_as_zero_count",
        "prohibited_output_field_count",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "semantic_drift_count",
        "product_doctrine_alignment_status",
        "cycle_state_machine_alignment_status",
        "product_capability_progress_ready",
        "product_capability_progress_impacted_count",
        "phase72_closure_status",
        "result",
    )
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
