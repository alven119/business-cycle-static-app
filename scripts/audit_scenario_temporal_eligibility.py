#!/usr/bin/env python
"""Audit scenario-level temporal eligibility."""

from __future__ import annotations

from business_cycle.audits.scenario_temporal_eligibility import (
    summarize_scenario_temporal_eligibility,
)


def main() -> int:
    summary = summarize_scenario_temporal_eligibility()
    for key, value in summary.items():
        if key == "scenarios":
            continue
        print(f"{key}={_format(value)}")
    for row in summary["scenarios"]:
        print(
            "scenario "
            f"scenario_id={row['scenario_id']} "
            f"temporal_tier={row['temporal_tier']} "
            f"strict_complete_as_of_count={row['strict_complete_as_of_count']} "
            f"strict_partial_as_of_count={row['strict_partial_as_of_count']} "
            f"formal_indicator_output_covered_count={row['formal_indicator_output_covered_count']} "
            f"formal_indicator_output_missing_count={row['formal_indicator_output_missing_count']} "
            f"coverage_ratio={row['coverage_ratio']} "
            f"calibration_allowed={_format(row['eligible_for_parameter_calibration'])} "
            f"validation_allowed={_format(row['eligible_for_validation'])} "
            f"holdout_allowed={_format(row['eligible_for_untouched_holdout'])} "
            f"performance_backtest_allowed={_format(row['eligible_for_historical_performance_backtest'])} "
            f"book_benchmark_allowed={_format(row['eligible_for_book_benchmark_reproduction'])} "
            f"missing_series_ids={','.join(row['missing_series_ids'])}"
        )
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
