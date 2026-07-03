#!/usr/bin/env python3
"""Show archive-regression shard plan readiness."""

from __future__ import annotations

from business_cycle.audits.archive_regression_shards import (
    summarize_archive_regression_shards,
)


def main() -> int:
    summary = summarize_archive_regression_shards()
    keys = [
        "archive_regression_shard_plan_ready",
        "phase_id",
        "phase_label",
        "archive_shard_count",
        "archive_shard_with_tests_count",
        "archive_file_count",
        "archive_file_coverage_complete",
        "archive_unassigned_test_file_count",
        "archive_duplicate_assignment_count",
        "legacy_v1_shard_test_file_count",
        "phase_closure_shard_test_file_count",
        "nightly_matrix_ready",
        "nightly_shard_count",
        "default_product_core_test_file_count",
        "live_optional_excluded_from_shards",
        "semantic_drift_count",
        "production_behavior_change_count",
        "result",
    ]
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    for row in summary["shard_rows"]:
        print(f"shard.{row['shard_id']}.test_file_count={row['test_file_count']}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
