from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.validation.post_comparability_validation_rerun import (
    build_post_comparability_validation_rerun,
    write_post_comparability_validation_rerun,
)


def test_post_comparability_validation_rerun_is_ready() -> None:
    run = build_post_comparability_validation_rerun()

    assert run["post_comparability_validation_rerun_ready"] is True
    assert run["updated_predicted_label_artifact_count"] == 5
    assert run["updated_comparison_artifact_count"] == 5
    assert run["updated_historical_accuracy_metric_count"] == 5
    assert run["updated_blockage_diagnostic_scenario_count"] == 5
    assert run["updated_scenario_trace_count"] == 5
    assert run["pre_blocked_scenario_count"] == 0
    assert run["post_blocked_scenario_count"] == 0
    assert run["pre_comparable_scenario_count"] == 0
    assert run["post_comparable_scenario_count"] == 2
    assert run["false_comparability_count"] == 0
    assert run["new_accuracy_metric_computed_count"] == 0
    assert run["economic_performance_metric_count"] == 0
    assert run["candidate_phase_emitted"] is False
    assert run["current_phase_emitted"] is False


def test_post_comparability_validation_rerun_writes_tmp_only(tmp_path: Path) -> None:
    result = write_post_comparability_validation_rerun(
        build_post_comparability_validation_rerun(),
        output_dir=tmp_path / "phase35_post_comparability",
    )

    assert result["post_comparability_validation_rerun_written"] is True
    assert result["research_artifact_explorer_written"] is True
    assert result["written_file_count"] == 9


def test_post_comparability_validation_rerun_rejects_repo_output() -> None:
    with pytest.raises(ValueError):
        write_post_comparability_validation_rerun(
            build_post_comparability_validation_rerun(),
            output_dir="data/backtests/phase35_post_comparability",
        )


def test_run_post_comparability_validation_rerun_script(tmp_path: Path) -> None:
    output_dir = tmp_path / "phase35_post_comparability"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_post_comparability_validation_rerun.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "post_comparability_validation_rerun_ready=true" in result.stdout
    assert "post_comparable_scenario_count=2" in result.stdout
    assert output_dir.is_dir()
