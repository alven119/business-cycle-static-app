from __future__ import annotations

import subprocess
import sys

from business_cycle.validation.post_evidence_completion_validation_rerun import (
    build_post_evidence_completion_validation_rerun,
    summarize_post_evidence_completion_validation_rerun,
)


def test_post_evidence_completion_validation_rerun_is_ready() -> None:
    summary = summarize_post_evidence_completion_validation_rerun()

    assert summary["post_evidence_completion_validation_rerun_ready"] is True
    assert summary["updated_research_decision_output_count"] == 5
    assert summary["updated_predicted_label_artifact_count"] == 5
    assert summary["updated_comparison_artifact_count"] == 5
    assert summary["updated_historical_accuracy_metric_count"] == 5
    assert summary["historical_validation_result_artifact_count"] == 1
    assert summary["pre_comparable_scenario_count"] == 2
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["false_comparability_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_post_evidence_completion_validation_rerun_script(tmp_path) -> None:
    output_dir = tmp_path / "post_completion"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_post_evidence_completion_validation_rerun.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (output_dir / "phase36r_post_completion_summary.json").exists()
    assert (output_dir / "phase36r_research_artifact_explorer.html").exists()
    assert "post_evidence_completion_validation_rerun_ready=true" in result.stdout


def test_post_evidence_completion_validation_rerun_keeps_research_only_bounds() -> None:
    run = build_post_evidence_completion_validation_rerun()

    assert run["completion_run"]["label_used_by_runtime_count"] == 0
    assert run["completion_run"]["evidence_rule_semantics_modified_count"] == 0
    assert run["completion_run"]["predicted_mapping_rule_modified_count"] == 0
    assert run["completion_run"]["formal_decision_contract_modified_count"] == 0
    assert run["completion_run"]["economic_performance_metric_count"] == 0
