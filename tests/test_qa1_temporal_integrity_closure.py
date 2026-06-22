from __future__ import annotations

from business_cycle.audits.qa1_temporal_integrity_closure import (
    summarize_qa1_temporal_integrity_closure,
)


def test_qa1_closes_with_explicit_gaps_and_limited_qa2_permission() -> None:
    summary = summarize_qa1_temporal_integrity_closure()

    assert summary["qa1_closure_status"] == "closed_with_explicit_historical_gaps"
    assert summary["qa1_scenario_eligibility_ready"] is True
    assert summary["qa1_strict_abstention_ready"] is True
    assert summary["qa1_formal_phase_decision_gate_ready"] is True
    assert summary["full_formal_history_ready"] is False
    assert summary["book_benchmark_temporal_ready"] is False
    assert summary["real_backtest_temporal_ready"] is False
    assert summary["qa2_allowed"] is True
    assert summary["qa2_performance_backtest_allowed"] is False
    assert summary["qa2_parameter_calibration_allowed"] is False
    assert summary["recommended_next_phase"] == "QA2"
