from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.validation.post_resolution_validation_rerun import (
    build_post_resolution_validation_rerun,
    write_post_resolution_validation_rerun,
)


def test_post_resolution_validation_rerun_is_ready() -> None:
    run = build_post_resolution_validation_rerun()

    assert run["post_resolution_validation_rerun_ready"] is True
    assert run["updated_predicted_label_artifact_count"] == 5
    assert run["updated_comparison_artifact_count"] == 5
    assert run["updated_historical_accuracy_metric_count"] == 5
    assert run["updated_blockage_diagnostic_scenario_count"] == 5
    assert run["updated_scenario_trace_count"] == 5
    assert run["pre_resolution_blocked_scenario_count"] == 5
    assert run["post_resolution_blocked_scenario_count"] == 5
    assert run["new_accuracy_metric_computed_count"] == 0
    assert run["economic_performance_metric_count"] == 0
    assert run["candidate_phase_emitted"] is False
    assert run["current_phase_emitted"] is False


def test_post_resolution_validation_rerun_writes_bundle_under_tmp(
    tmp_path: Path,
) -> None:
    result = write_post_resolution_validation_rerun(
        build_post_resolution_validation_rerun(),
        output_dir=tmp_path / "phase33_post_resolution",
    )

    assert result["post_resolution_validation_rerun_written"] is True
    assert result["research_artifact_explorer_written"] is True
    assert result["written_file_count"] == 8
    for path in result["written_files"]:
        assert Path(path).is_file()


def test_post_resolution_validation_rerun_rejects_repo_output() -> None:
    with pytest.raises(ValueError):
        write_post_resolution_validation_rerun(
            build_post_resolution_validation_rerun(),
            output_dir="data/backtests/phase33_post_resolution",
        )


def test_run_post_resolution_validation_rerun_script(tmp_path: Path) -> None:
    output_dir = tmp_path / "phase33_post_resolution"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_post_resolution_validation_rerun.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "post_resolution_validation_rerun_ready=true" in result.stdout
    assert "updated_historical_accuracy_metric_count=5" in result.stdout
    assert (output_dir / "phase33_research_artifact_explorer.html").is_file()
