#!/usr/bin/env python3
"""Show default-suite reduction plan readiness."""

from __future__ import annotations

from business_cycle.audits.test_suite_reduction_plan import (
    summarize_test_suite_reduction_plan,
)


def main() -> int:
    summary = summarize_test_suite_reduction_plan()
    keys = [
        "test_suite_reduction_plan_ready",
        "phase_id",
        "phase_label",
        "default_product_core_test_file_count",
        "default_product_core_max_file_count",
        "default_pytest_selected_file_count_within_limit",
        "archive_regression_marker_registered",
        "archive_regression_tests_not_in_default_ci",
        "archive_regression_test_count",
        "closure_archive_test_count",
        "legacy_v1_default_test_count",
        "v1_default_removed",
        "product_core_capability_mapping_ready",
        "c1_core_tests_present",
        "c2_core_tests_present",
        "c3_core_tests_present",
        "dashboard_core_tests_present",
        "live_optional_tests_not_in_default_ci",
        "semantic_drift_count",
        "production_behavior_change_count",
        "result",
    ]
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
