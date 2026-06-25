from __future__ import annotations

import subprocess
import sys

from business_cycle.validation.historical_comparability_diagnostics import (
    summarize_historical_comparability_diagnostics,
)


def test_historical_comparability_diagnostics_are_ready() -> None:
    summary = summarize_historical_comparability_diagnostics()

    assert summary["historical_comparability_diagnostics_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["pre_blocked_scenario_count"] == 0
    assert summary["post_blocked_scenario_count"] == 0
    assert summary["pre_comparable_scenario_count"] == 0
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["remaining_non_comparable_scenario_count"] == 3
    assert summary["false_comparability_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["new_accuracy_metric_computed_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    artifact = summary["historical_comparability_diagnostics_artifact"]
    assert artifact["post_comparison_status_summary"]["comparable"] == 2
    assert artifact["post_comparison_status_summary"]["abstained"] == 3


def test_show_historical_comparability_diagnostics_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_historical_comparability_diagnostics.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "historical_comparability_diagnostics_ready=true" in result.stdout
    assert "post_comparable_scenario_count=2" in result.stdout
