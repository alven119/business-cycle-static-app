from __future__ import annotations

import subprocess
import sys

from business_cycle.portfolio.cash_flow_backtest_kernel_contract import (
    build_cash_flow_backtest_kernel_view_model,
    load_cash_flow_backtest_kernel_contract,
    summarize_cash_flow_backtest_kernel_contract,
)


def test_phase78_cash_flow_backtest_kernel_contract_passes() -> None:
    summary = summarize_cash_flow_backtest_kernel_contract()

    assert summary["result"] == "passed"
    assert summary["cash_flow_aware_backtest_kernel_contract_ready"] is True
    assert summary["kernel_component_count"] == 10
    assert summary["required_kernel_component_count"] == 10
    assert summary["structural_fixture_count"] == 3
    assert summary["structural_fixture_validation_pass_count"] == 3
    assert summary["execution_allowed_now_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_count"] == 0
    assert summary["generated_output_under_tmp_only"] is True
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["live_allocation_output_count"] == 0
    assert summary["prohibited_kernel_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_phase78_kernel_components_are_contract_only() -> None:
    contract = load_cash_flow_backtest_kernel_contract()

    assert contract.output_policy["output_mode"] == "research_kernel_contract_only"
    assert contract.output_policy["execution_allowed_now"] is False
    assert contract.output_policy["metric_computation_allowed_now"] is False
    assert contract.output_policy["backtest_execution_allowed"] is False
    assert contract.output_policy["generated_output_under_tmp_only"] is True
    for component in contract.kernel_components:
        assert component["compute_allowed_now"] is False
        assert component["output_allowed_now"] == "structural_contract_only"
        assert component["required_inputs"]
        assert component["required_guards"]
    for fixture in contract.structural_fixtures:
        assert fixture["output_path_policy"] == "tmp_only"
        assert fixture["metric_values_allowed"] is False
        assert fixture["expected_status"].endswith("_no_execution")


def test_phase78_kernel_view_model_is_non_executing() -> None:
    view_model = build_cash_flow_backtest_kernel_view_model()

    assert view_model["view_id"] == "cash_flow_aware_backtest_kernel_contract"
    assert view_model["research_only"] is True
    assert view_model["output_mode"] == "research_kernel_contract_only"
    assert view_model["execution_allowed_now"] is False
    assert view_model["metric_computation_enabled"] is False
    assert len(view_model["kernel_components"]) == 10
    assert view_model["trust_metadata"]["generated_output_under_tmp_only"] is True
    assert view_model["trust_metadata"]["backtest_execution_enabled"] is False
    assert view_model["trust_metadata"]["trade_signal_enabled"] is False
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False


def test_show_cash_flow_backtest_kernel_contract_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_cash_flow_backtest_kernel_contract.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "cash_flow_aware_backtest_kernel_contract_ready=true" in completed.stdout
    assert "kernel_component_count=10" in completed.stdout
    assert "backtest_execution_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
