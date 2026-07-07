from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from business_cycle.audits.archive_regression_shards import (
    SHARD_IDS,
    assign_archive_shard,
    pytest_command_for_shard,
    shard_test_files,
    summarize_archive_regression_shards,
)


def test_archive_regression_shard_plan_passes() -> None:
    summary = summarize_archive_regression_shards()

    assert summary["result"] == "passed"
    assert summary["archive_regression_shard_plan_ready"] is True
    assert summary["archive_shard_count"] == 8
    assert summary["archive_shard_with_tests_count"] == 8
    assert summary["archive_file_coverage_complete"] is True
    assert summary["archive_unassigned_test_file_count"] == 0
    assert summary["archive_duplicate_assignment_count"] == 0
    assert summary["legacy_v1_shard_test_file_count"] > 0
    assert summary["phase_closure_shard_test_file_count"] > 0
    assert summary["nightly_matrix_ready"] is True
    assert summary["nightly_shard_count"] == 8
    assert summary["default_product_core_test_file_count"] == 29
    assert summary["live_optional_excluded_from_shards"] is True
    assert summary["semantic_drift_count"] == 0
    assert summary["production_behavior_change_count"] == 0


def test_archive_shard_assignment_is_stable_for_representative_tests() -> None:
    assert (
        assign_archive_shard("tests/test_phase_scoring.py")
        == "legacy_v1_compatibility"
    )
    assert (
        assign_archive_shard("tests/test_phase20_historical_validation_dry_run_closure.py")
        == "phase_closure_history"
    )
    assert (
        assign_archive_shard("tests/test_historical_accuracy_metrics.py")
        == "historical_validation_replay"
    )
    assert (
        assign_archive_shard("tests/test_transition_timing_replay_preview.py")
        == "historical_validation_replay"
    )
    assert (
        assign_archive_shard("tests/test_portfolio_policy_template_schema.py")
        == "portfolio_policy_research"
    )


def test_each_archive_shard_has_files_and_excludes_live_optional() -> None:
    for shard_id in SHARD_IDS:
        files = shard_test_files(shard_id)
        assert files
        assert all("live_refresh" not in path for path in files)


def test_pytest_command_for_archive_shard_uses_current_interpreter() -> None:
    command = pytest_command_for_shard("legacy_v1_compatibility", collect_only=True)

    assert command[0] == sys.executable
    assert "-o" in command
    assert "addopts=" in command
    assert "archive_regression and not live_optional" in command
    assert "--collect-only" in command


def test_archive_regression_shard_script_collects_legacy_shard() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_archive_regression_shard.py",
            "--shard",
            "legacy_v1_compatibility",
            "--collect-only",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "tests/test_phase_scoring.py::" in completed.stdout


def test_archive_regression_shards_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_archive_regression_shards.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "archive_regression_shard_plan_ready=true" in completed.stdout
    assert "archive_shard_count=8" in completed.stdout
    assert "nightly_matrix_ready=true" in completed.stdout
    assert "result=passed" in completed.stdout


def test_archive_regression_shard_plan_documented() -> None:
    doc = Path("docs/archive_regression_shard_plan_phase66.md").read_text(
        encoding="utf-8"
    )

    assert "legacy_v1_compatibility" in doc
    assert "phase_closure_history" in doc
    assert "Product Capability Impact" in doc
    assert "does not raise product capability percentages" in doc
