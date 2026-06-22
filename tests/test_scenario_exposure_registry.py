from __future__ import annotations

from business_cycle.audits.scenario_exposure import summarize_scenario_exposure_registry


def test_current_five_scenarios_are_development_only() -> None:
    summary = summarize_scenario_exposure_registry()

    assert summary["scenario_exposure_registry_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["previously_seen_scenario_count"] == 5
    assert summary["development_scenario_count"] == 5
    assert summary["independent_validation_scenario_count"] == 0
    assert summary["untouched_holdout_scenario_count"] == 0
    assert summary["performance_claim_eligible_scenario_count"] == 0
    assert summary["scenario_without_exposure_history_count"] == 0
    assert summary["scenario_incorrectly_marked_out_of_sample_count"] == 0
    assert summary["scenario_incorrectly_marked_holdout_count"] == 0
