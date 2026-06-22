from __future__ import annotations

from business_cycle.audits.scenario_temporal_eligibility import (
    summarize_scenario_temporal_eligibility,
)


def test_scenario_temporal_eligibility_blocks_incomplete_uses() -> None:
    summary = summarize_scenario_temporal_eligibility()

    assert summary["scenario_count"] == 5
    assert summary["scenario_as_of_universe_consistent"] is True
    assert summary["scenario_with_silent_horizon_reduction_count"] == 0
    assert summary["incomplete_scenario_marked_strict_complete_count"] == 0
    assert summary["strict_partial_scenario_marked_performance_eligible_count"] == 0
    assert summary["previously_observed_scenario_marked_untouched_holdout_count"] == 0
    rows = {row["scenario_id"]: row for row in summary["scenarios"]}
    assert rows["dotcom_bubble"]["temporal_tier"] == "strict_partial"
    assert rows["dotcom_bubble"]["eligible_for_historical_performance_backtest"] is False
    assert rows["covid_recession"]["temporal_tier"] == "strict_complete"
