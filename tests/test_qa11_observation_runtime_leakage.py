from __future__ import annotations

from business_cycle.audits.qa11_observation_runtime_leakage import (
    summarize_qa11_observation_runtime_leakage,
)


def test_qa11_observation_runtime_leakage_counts_are_zero() -> None:
    summary = summarize_qa11_observation_runtime_leakage()

    assert summary["leakage_guard_ready"] is True
    assert summary["scenario_id_reference_count"] == 0
    assert summary["historical_date_reference_count"] == 0
    assert summary["expected_label_reference_count"] == 0
    assert summary["nber_reference_count"] == 0
    assert summary["portfolio_return_reference_count"] == 0
    assert summary["copied_historical_threshold_count"] == 0
    assert summary["contextual_250k_executable_use_count"] == 0

