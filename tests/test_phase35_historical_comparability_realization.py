from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase35_historical_comparability_realization import (
    summarize_phase35_historical_comparability_realization,
)


def test_phase35_historical_comparability_realization_passes() -> None:
    summary = summarize_phase35_historical_comparability_realization()

    assert summary["result"] == "passed"
    assert summary["autonomous_comparability_realization_ready"] is True
    assert summary["post_comparability_validation_rerun_ready"] is True
    assert summary["historical_comparability_diagnostics_ready"] is True
    assert summary["pre_blocked_scenario_count"] == 0
    assert summary["post_blocked_scenario_count"] == 0
    assert summary["pre_comparable_scenario_count"] == 0
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["development_next_phase"] == 36
    assert summary["phase35_comparability_progress_status"] == (
        "comparable_scenarios_realized"
    )


def test_show_phase35_historical_comparability_realization_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase35_historical_comparability_realization.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "post_comparable_scenario_count=2" in result.stdout
    assert "result=passed" in result.stdout
