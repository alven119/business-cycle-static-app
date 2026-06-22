from __future__ import annotations

from business_cycle.audits.qa2_context_ablation_closure import (
    summarize_qa2_context_ablation_closure,
)


def test_qa2_closes_context_dependency_measurement_without_backtest() -> None:
    summary = summarize_qa2_context_ablation_closure()

    assert summary["result"] == "passed"
    assert summary["qa2_closure_status"] == "closed_context_dependency_measured"
    assert summary["data_only_path_structurally_validated"] is True
    assert summary["data_only_model_economically_validated"] is False
    assert summary["production_context_dependency_measured"] is True
    assert summary["production_default_preserved"] is True
    assert summary["qa2_performance_backtest_executed"] is False
    assert summary["qa2_parameter_calibration_executed"] is False
    assert summary["recommended_next_phase"] == "QA3"
