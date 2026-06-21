from __future__ import annotations

from business_cycle.audits import summarize_calibration_integrity


def test_current_scenarios_are_development_diagnostics_not_final_holdout() -> None:
    summary = summarize_calibration_integrity()

    assert summary["scenario_count"] == 5
    assert summary["development_scenario_count"] == 5
    assert summary["untouched_holdout_scenario_count"] == 0
    assert summary["previously_seen_scenario_count"] == 5
    assert summary["calibration_holdout_ready"] is False
    assert summary["out_of_sample_claim_allowed"] is False

