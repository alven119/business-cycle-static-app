#!/usr/bin/env python3
"""Show Phase74 local current-cache dashboard bridge readiness."""

from __future__ import annotations

import argparse

from business_cycle.render.local_current_cache_dashboard_bridge import (
    summarize_local_current_cache_dashboard_bridge,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache-dir",
        help=(
            "Explicit local current cache under /tmp or "
            "data/raw/fred_current_cache. Omit to run tmp seeded rehearsal."
        ),
    )
    parser.add_argument("--snapshot-as-of", default="2026-07-03")
    args = parser.parse_args()

    summary = summarize_local_current_cache_dashboard_bridge(
        cache_dir=args.cache_dir,
        snapshot_as_of=args.snapshot_as_of,
    )
    keys = [
        "phase",
        "local_current_cache_dashboard_bridge_ready",
        "local_current_cache_input_supported",
        "tmp_seeded_local_current_cache_rehearsal_ready",
        "role_count",
        "role_with_official_series_count",
        "role_without_official_series_count",
        "unique_official_series_count",
        "local_cache_series_file_found_count",
        "role_with_local_cache_numeric_context_count",
        "role_with_available_local_cache_chart_count",
        "role_with_ytd_available_local_cache_chart_count",
        "role_with_trailing_1y_available_local_cache_chart_count",
        "role_with_trailing_5y_available_local_cache_chart_count",
        "local_cache_unavailable_role_count",
        "local_cache_chart_point_count",
        "cache_scope",
        "cache_dir_kind",
        "data_mode",
        "repo_output_written_count",
        "local_cache_written_by_bridge_count",
        "fixture_mislabeled_as_live_count",
        "local_cache_value_mislabeled_as_point_in_time_count",
        "numeric_context_promoted_to_phase_support_count",
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
        "result",
    ]
    for key in keys:
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
