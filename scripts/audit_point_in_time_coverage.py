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
        "formal_leaf_direct_dependency_count",
        "formal_derived_output_count",
        "formal_leaf_total_pair_count",
        "formal_leaf_covered_pair_count",
        "formal_leaf_missing_pair_count",
        "formal_leaf_coverage_ratio",
        "formal_derived_output_total_pair_count",
        "formal_derived_candidate_pair_count",
        "formal_derived_strict_covered_pair_count",
        "formal_derived_strict_coverage_ratio",
        "formal_exact_vintage_dependency_count",
        "formal_missing_vintage_dependency_count",
        "formal_scenario_as_of_date_count",
        "formal_scenario_as_of_covered_count",
        "formal_total_coverage_pair_count",
        "formal_leaf_total_coverage_pair_count",
        "formal_derived_total_coverage_pair_count",
        "formal_covered_pair_count",
        "formal_missing_pair_count",
        "formal_leaf_covered_pair_count",
        "formal_leaf_missing_pair_count",
        "formal_derived_covered_pair_count",
        "formal_derived_missing_pair_count",
        "candidate_derived_snapshot_count",
        "provisional_derived_snapshot_count",
        "provisional_snapshot_counted_as_strict_count",
        "formal_indicator_output_counting_ready",
        "formal_proxy_pair_count",
        "formal_initial_release_only_pair_count",
        "formal_revised_fallback_pair_count",
        "formal_invalid_realtime_interval_count",
        "strict_snapshot_validation_failure_count",
        "exact_vintage_covered_pair_count",
        "release_archive_covered_pair_count",
        "observational_archive_covered_pair_count",
        "derived_point_in_time_covered_pair_count",
        "duplicate_temporal_pair_id_count",
        "derived_output_double_count_count",
        "denominator_semantics_valid",
        "formal_scenario_as_of_coverage_ratio",
        "date_local_strict_ready_snapshot_count",
        "partial_horizon_strict_ready_series_count",
        "full_horizon_blocked_but_date_local_ready_series_count",
        "series_with_authoritative_cache_count",
        "series_with_valid_manifest_count",
        "series_with_segmented_cache_count",
        "segment_merge_failure_count",
        "dgs10_required_pair_count",
        "dgs10_covered_pair_count",
        "dgs10_missing_pair_count",
        "dgs10_coverage_ratio",
        "dgs10_partial_horizon_ready",
        "dgs10_full_required_horizon_ready",
        "dgs10_first_covered_as_of",
        "dgs10_last_covered_as_of",
        "dgs10_first_missing_as_of",
        "dgs10_last_missing_as_of",
        "blocker_class",
        "official_query_supported_series_count",
        "official_query_attempted_series_count",
        "official_query_succeeded_series_count",
        "official_query_failed_series_count",
        "partial_vintage_history_series_count",
        "full_required_horizon_exact_vintage_series_count",
        "full_required_horizon_archive_reconstructed_series_count",
        "full_required_horizon_observational_series_count",
        "full_required_horizon_strict_ready_series_count",
        "history_insufficient_series_count",
        "provider_full_range_failed_series_count",
        "unresolved_formal_series_count",
        "registry_declared_exact_vintage_series_count",
        "live_verified_exact_vintage_series_count",
        "live_verified_initial_release_series_count",
        "live_verified_unsupported_series_count",
        "live_verified_history_insufficient_series_count",
        "official_archive_network_attempted_count",
        "official_archive_artifact_downloaded_count",
        "official_archive_structured_response_count",
        "official_archive_parse_attempted_count",
        "official_archive_parse_succeeded_count",
        "official_archive_parsed_release_count",
        "official_archive_extracted_row_count",
        "official_archive_as_of_snapshot_count",
        "placeholder_only_archive_entry_count",
        "archive_entry_without_artifact_count",
        "archive_entry_without_parsed_rows_count",
        "implemented_archive_entry_without_artifact_count",
        "implemented_archive_entry_without_parsed_rows_count",
        "strict_snapshot_without_artifact_provenance_count",
        "strict_snapshot_without_availability_date_count",
        "strict_snapshot_without_parser_version_count",
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
    if summary["unresolved_formal_series_ids"]:
        print("unresolved_formal_series_ids=" + ",".join(summary["unresolved_formal_series_ids"]))
    return 0 if summary["result"] in {"passed", "blocked"} else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
