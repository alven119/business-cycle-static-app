from __future__ import annotations

import subprocess
import sys

from business_cycle.validation.post_pit_remediation_validation_rerun import (
    build_post_pit_remediation_validation_rerun,
    summarize_post_pit_remediation_validation_rerun,
    write_post_pit_remediation_validation_rerun,
)


def test_post_pit_remediation_validation_rerun_preserves_metric_scope() -> None:
    summary = summarize_post_pit_remediation_validation_rerun()

    assert summary["post_pit_remediation_validation_rerun_ready"] is True
    assert summary["updated_research_decision_output_count"] == 5
    assert summary["updated_predicted_label_artifact_count"] == 5
    assert summary["updated_comparison_artifact_count"] == 5
    assert summary["updated_historical_accuracy_metric_count"] == 5
    assert summary["new_accuracy_metric_computed_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_post_pit_remediation_validation_rerun_writes_bundle_under_tmp(
    tmp_path,
) -> None:
    write = write_post_pit_remediation_validation_rerun(
        build_post_pit_remediation_validation_rerun(),
        output_dir=tmp_path,
    )

    assert write["post_pit_remediation_validation_rerun_written"] is True
    assert (tmp_path / "phase37_pit_gap_matrix.json").is_file()
    assert (tmp_path / "phase37_pit_remediation.json").is_file()
    assert (tmp_path / "phase37_research_artifact_explorer.html").is_file()
    assert write["forbidden_repo_output_count"] == 0


def test_run_post_pit_remediation_validation_rerun_script(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_post_pit_remediation_validation_rerun.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "post_pit_remediation_validation_rerun_ready=true" in result.stdout
    assert "result=passed" in result.stdout
