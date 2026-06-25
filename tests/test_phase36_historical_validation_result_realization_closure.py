from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase36_historical_validation_result_realization_closure import (
    summarize_phase36_historical_validation_result_realization_closure,
)


def test_phase36_historical_validation_result_realization_closure_passes() -> None:
    summary = summarize_phase36_historical_validation_result_realization_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["historical_validation_result_runtime_ready"] is True
    assert summary["recession_recovery_comparability_unblock_ready"] is True
    assert summary["post_validation_result_rerun_ready"] is True
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["historical_validation_result_artifact_count"] == 1
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["alpha32_freeze_hash_valid"] is True
    assert summary["alpha31_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["economic_validation_status"] == (
        "historical_validation_results_generated_research_only_no_performance"
    )
    assert summary["development_next_phase"] == "PHASE_36_REVIEW"
    assert summary["phase36_closure_status"] == (
        "closed_historical_validation_results_generated_remaining_recession_recovery_"
        "genuine_non_comparable"
    )


def test_show_phase36_historical_validation_result_realization_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase36_historical_validation_result_realization_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase36_closure_status=" in result.stdout
    assert "result=passed" in result.stdout
