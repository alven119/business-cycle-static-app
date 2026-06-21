#!/usr/bin/env python
"""Audit QA1 point-in-time metadata and cache coverage."""

from __future__ import annotations

import argparse

from business_cycle.audits.point_in_time_coverage import summarize_point_in_time_coverage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", default="data/raw/fred_vintages")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = summarize_point_in_time_coverage(cache_dir=args.cache_dir)
    keys = (
        "discovered_unique_series_count",
        "availability_metadata_complete_count",
        "exact_vintage_supported_series_count",
        "initial_release_only_series_count",
        "release_lag_proxy_series_count",
        "unsupported_series_count",
        "cached_series_count",
        "formal_indicator_count",
        "formal_direct_dependency_count",
        "formal_derived_dependency_count",
        "formal_exact_vintage_dependency_count",
        "formal_missing_vintage_dependency_count",
        "formal_scenario_as_of_date_count",
        "formal_scenario_as_of_covered_count",
        "formal_total_coverage_pair_count",
        "formal_covered_pair_count",
        "formal_missing_pair_count",
        "formal_proxy_pair_count",
        "formal_initial_release_only_pair_count",
        "formal_revised_fallback_pair_count",
        "formal_invalid_realtime_interval_count",
        "strict_snapshot_validation_failure_count",
        "formal_scenario_as_of_coverage_ratio",
        "blocker_class",
        "official_query_attempted_series_count",
        "official_query_succeeded_series_count",
        "official_query_failed_series_count",
        "registry_declared_exact_vintage_series_count",
        "live_verified_exact_vintage_series_count",
        "live_verified_initial_release_series_count",
        "live_verified_unsupported_series_count",
        "live_verified_history_insufficient_series_count",
        "experimental_exact_vintage_coverage_ratio",
        "point_in_time_selector_ready",
        "formal_phase_point_in_time_ready",
        "all_experimental_point_in_time_ready",
        "golden_benchmark_point_in_time_ready",
        "no_silent_revised_fallback",
        "release_lag_proxy_misclassified_as_point_in_time_count",
        "availability_precision_day_count",
        "availability_precision_unknown_count",
        "alfred_ingestion_lag_caveat_present",
        "point_in_time_backtest_ready",
        "book_alignment_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "recommended_next_phase",
        "result",
    )
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    if summary["formal_missing_vintage_dependency_series_ids"]:
        print(
            "formal_missing_vintage_dependency_series_ids="
            + ",".join(summary["formal_missing_vintage_dependency_series_ids"])
        )
    return 0 if summary["result"] in {"passed", "blocked"} else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
