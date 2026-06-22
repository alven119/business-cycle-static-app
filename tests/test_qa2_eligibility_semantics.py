from __future__ import annotations

from business_cycle.audits.scenario_temporal_eligibility import (
    summarize_scenario_temporal_eligibility,
)


def test_temporal_methodological_and_final_eligibility_are_separate() -> None:
    summary = summarize_scenario_temporal_eligibility()

    assert summary["temporally_eligible_for_parameter_calibration_scenario_count"] == 2
    assert summary["previously_seen_scenario_count"] == 5
    assert summary["final_validation_eligible_scenario_count"] == 0
    assert summary["final_untouched_holdout_eligible_scenario_count"] == 0
    assert summary["final_performance_backtest_eligible_scenario_count"] == 0
    assert summary["ambiguous_eligibility_field_count"] == 0
    assert summary["unscoped_performance_flag_count"] == 0
