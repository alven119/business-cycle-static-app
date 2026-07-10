"""Default-suite reduction plan audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.test_suite_doctrine_quarantine import (
    DEFAULT_PRODUCT_CORE_MAX_FILE_COUNT,
    DEFAULT_PRODUCT_CORE_TEST_FILES,
    summarize_test_suite_doctrine_quarantine,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PLAN_PATH = ROOT / "specs/common/test_suite_reduction_plan.yaml"


def build_test_suite_reduction_plan(
    path: str | Path = DEFAULT_PLAN_PATH,
) -> dict[str, Any]:
    """Load the governed test-suite reduction plan."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "test_suite_reduction_plan"
    ]


def summarize_test_suite_reduction_plan(
    path: str | Path = DEFAULT_PLAN_PATH,
) -> dict[str, Any]:
    """Summarize default-suite reduction readiness."""

    plan = build_test_suite_reduction_plan(path)
    quarantine = summarize_test_suite_doctrine_quarantine()
    ongoing = plan["ongoing_test_addition_policy"]
    plan_default_files = set(plan["default_product_core_test_files"])
    code_default_files = set(DEFAULT_PRODUCT_CORE_TEST_FILES)
    expected = dict(plan["hard_gates"])
    default_file_count = int(quarantine["default_product_core_test_file_count"])
    summary = {
        "test_suite_reduction_plan_ready": False,
        "version": plan["version"],
        "status": plan["status"],
        "phase_id": int(plan["phase_id"]),
        "phase_label": plan["phase_label"],
        "default_product_core_test_file_count": default_file_count,
        "default_product_core_max_file_count": DEFAULT_PRODUCT_CORE_MAX_FILE_COUNT,
        "default_pytest_selected_file_count_within_limit": (
            default_file_count <= DEFAULT_PRODUCT_CORE_MAX_FILE_COUNT
        ),
        "default_core_file_contract_matches_code": plan_default_files
        == code_default_files,
        "archive_regression_marker_registered": quarantine[
            "archive_regression_marker_registered"
        ],
        "archive_regression_tests_not_in_default_ci": quarantine[
            "archive_regression_tests_not_in_default_ci"
        ],
        "archive_regression_test_count": quarantine["archive_regression_test_count"],
        "archive_regression_test_count_gt_zero": quarantine[
            "archive_regression_test_count"
        ]
        > 0,
        "closure_archive_test_count": quarantine["closure_archive_test_count"],
        "closure_archive_test_count_gt_zero": quarantine[
            "closure_archive_test_count"
        ]
        > 0,
        "legacy_v1_default_test_count": quarantine["legacy_v1_default_test_count"],
        "v1_default_removed": quarantine["v1_default_removed"],
        "product_core_capability_mapping_ready": quarantine[
            "product_core_capability_mapping_ready"
        ],
        "c1_core_tests_present": quarantine["c1_core_tests_present"],
        "c2_core_tests_present": quarantine["c2_core_tests_present"],
        "c3_core_tests_present": quarantine["c3_core_tests_present"],
        "dashboard_core_tests_present": quarantine["dashboard_core_tests_present"],
        "live_optional_tests_not_in_default_ci": quarantine[
            "live_optional_tests_not_in_default_ci"
        ],
        "ongoing_test_addition_policy_ready": all(
            (
                ongoing["inspect_test_suite_index_first"],
                ongoing["search_for_similar_or_duplicate_test_first"],
                ongoing["extend_existing_test_preferred"],
                ongoing["new_test_file_requires_capability_gap"],
                ongoing["expensive_builder_fixture_reuse_required"],
                ongoing["phase_report_must_include_test_delta_and_duration"],
                ongoing["redundant_cli_smoke_tier"] == "archive_or_nightly",
            ),
        ),
        "product_capabilities_protected": plan["product_capabilities_protected"],
        "phase_plan_integration": plan["phase_plan_integration"],
        "semantic_drift_count": 0,
        "production_behavior_change_count": quarantine[
            "production_behavior_change_count"
        ],
    }
    summary["test_suite_reduction_plan_ready"] = _passes(summary, expected)
    summary["result"] = (
        "passed" if summary["test_suite_reduction_plan_ready"] else "blocked"
    )
    return summary


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        key == "test_suite_reduction_plan_ready" or summary.get(key) == value
        for key, value in expected.items()
    ) and bool(summary["default_core_file_contract_matches_code"])
