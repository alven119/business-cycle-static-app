from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from business_cycle.audits.test_suite_reduction_plan import (
    summarize_test_suite_reduction_plan,
)


def test_test_suite_reduction_plan_passes() -> None:
    summary = summarize_test_suite_reduction_plan()

    assert summary["result"] == "passed"
    assert summary["test_suite_reduction_plan_ready"] is True
    assert summary["default_product_core_test_file_count"] == 29
    assert summary["default_product_core_max_file_count"] == 30
    assert summary["default_pytest_selected_file_count_within_limit"] is True
    assert summary["archive_regression_marker_registered"] is True
    assert summary["archive_regression_tests_not_in_default_ci"] is True
    assert summary["archive_regression_test_count"] > 0
    assert summary["closure_archive_test_count"] > 0
    assert summary["legacy_v1_default_test_count"] == 0
    assert summary["v1_default_removed"] is True
    assert summary["c1_core_tests_present"] is True
    assert summary["c2_core_tests_present"] is True
    assert summary["c3_core_tests_present"] is True
    assert summary["dashboard_core_tests_present"] is True
    assert summary["semantic_drift_count"] == 0
    assert summary["production_behavior_change_count"] == 0


def test_default_pytest_collects_only_product_core_files() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        check=True,
        capture_output=True,
        text=True,
    )
    collected_files = {
        line.split("::", 1)[0]
        for line in result.stdout.splitlines()
        if line.startswith("tests/test_") and "::" in line
    }

    assert collected_files
    assert len(collected_files) <= 30
    assert "tests/test_phase_scoring.py" not in collected_files
    assert "tests/test_transition_timing_replay_preview.py" not in collected_files
    assert "tests/test_phase20_historical_validation_dry_run_closure.py" not in (
        collected_files
    )


def test_archive_regression_collects_legacy_and_closure_tests() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-o",
            "addopts=",
            "-m",
            "archive_regression and not live_optional",
            "--collect-only",
            "-q",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "tests/test_phase_scoring.py::" in result.stdout
    assert "tests/test_transition_timing_replay_preview.py::" in result.stdout
    assert "tests/test_phase20_historical_validation_dry_run_closure.py::" in (
        result.stdout
    )


def test_test_suite_reduction_plan_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_test_suite_reduction_plan.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "test_suite_reduction_plan_ready=true" in completed.stdout
    assert "default_product_core_test_file_count=29" in completed.stdout
    assert "legacy_v1_default_test_count=0" in completed.stdout
    assert "result=passed" in completed.stdout


def test_phase_closure_tests_are_documented_as_archive_seals() -> None:
    doc = Path("docs/test_suite_reduction_plan_phase65.md").read_text(
        encoding="utf-8"
    )

    assert "Phase closure tests" in doc
    assert "historical acceptance seals" in doc
    assert "archive regression" in doc
