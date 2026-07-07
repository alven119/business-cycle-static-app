#!/usr/bin/env python3
"""Show GitHub Actions test-efficiency readiness."""

from __future__ import annotations

from business_cycle.audits.github_actions_test_efficiency import (
    summarize_github_actions_test_efficiency,
)


def main() -> int:
    summary = summarize_github_actions_test_efficiency()
    keys = (
        "github_actions_test_efficiency_ready",
        "workflow_yaml_parseable_count",
        "dependency_cache_workflow_count",
        "concurrency_workflow_count",
        "fast_ci_critical_subset_ready",
        "fast_ci_uses_contract_test_runner",
        "required_fast_ci_missing_test_count",
        "required_fast_ci_duplicate_test_count",
        "full_ci_uses_default_product_core_pytest",
        "nightly_ci_uses_archive_shard_matrix",
        "nightly_archive_shard_count",
        "nightly_monolithic_archive_pytest_count",
        "default_product_core_test_file_count",
        "archive_shard_count",
        "workflow_git_mutation_count",
        "safety_scan_workflow_count",
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
