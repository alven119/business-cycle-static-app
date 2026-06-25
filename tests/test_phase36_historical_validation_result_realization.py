from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase36_historical_validation_result_realization import (
    summarize_phase36_historical_validation_result_realization,
)


def test_phase36_historical_validation_result_realization_passes() -> None:
    summary = summarize_phase36_historical_validation_result_realization()

    assert summary["result"] == "passed"
    assert summary["historical_validation_result_runtime_ready"] is True
    assert summary["recession_recovery_comparability_unblock_ready"] is True
    assert summary["post_validation_result_rerun_ready"] is True
    assert summary["attempted_fix_iteration_count"] == 2
    assert summary["pre_comparable_scenario_count"] == 2
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["comparable_scenario_count"] == 2
    assert summary["historical_validation_result_artifact_count"] == 1
    assert summary["safe_fixable_recession_recovery_gap_count"] == 0
    assert summary["false_comparability_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["development_next_phase"] == "PHASE_36_REVIEW"


def test_show_phase36_historical_validation_result_realization_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase36_historical_validation_result_realization.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "historical_validation_result_runtime_ready=true" in result.stdout
    assert "recession_recovery_comparability_unblock_ready=true" in result.stdout
    assert "result=passed" in result.stdout
