#!/usr/bin/env python3
"""Show dynamic test-suite index readiness."""

from __future__ import annotations

from business_cycle.audits.test_suite_index import summarize_test_suite_index


def main() -> int:
    summary = summarize_test_suite_index()
    keys = (
        "test_suite_index_ready",
        "discovered_test_file_count",
        "indexed_test_file_count",
        "indexed_test_file_count_equals_discovered",
        "default_product_core_test_file_count",
        "default_product_core_indexed_count",
        "archive_regression_test_file_count",
        "live_optional_test_file_count",
        "duplicate_test_guard_key_count",
        "similar_test_reference_count",
        "new_test_preflight_policy_ready",
        "similar_test_extension_policy_ready",
        "product_capability_mapping_complete",
        "production_behavior_change_count",
        "semantic_drift_count",
        "result",
    )
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
