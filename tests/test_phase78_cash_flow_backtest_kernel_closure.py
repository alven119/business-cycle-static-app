from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase78_cash_flow_backtest_kernel_closure import (
    summarize_phase78_cash_flow_backtest_kernel_closure,
)


def test_phase78_cash_flow_backtest_kernel_closure_passes() -> None:
    summary = summarize_phase78_cash_flow_backtest_kernel_closure()

    assert summary["result"] == "passed"
    assert summary["phase78_closure_ready"] is True
    assert summary["cash_flow_aware_backtest_kernel_contract_ready"] is True
    assert summary["portfolio_policy_replay_schedule_contract_ready"] is True
    assert summary["kernel_component_count"] == 10
    assert summary["structural_fixture_validation_pass_count"] == 3
    assert summary["execution_allowed_now_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_count"] == 0
    assert summary["generated_output_under_tmp_only"] is True
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["live_allocation_output_count"] == 0
    assert summary["investment_advice_wording_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["phase78_closure_status"]
        == "closed_cash_flow_backtest_kernel_contract_ready_no_execution_or_metrics"
    )


def test_show_phase78_cash_flow_backtest_kernel_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_phase78_cash_flow_backtest_kernel_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase78_closure_ready=true" in completed.stdout
    assert "kernel_component_count=10" in completed.stdout
    assert "metric_computation_enabled=false" in completed.stdout
    assert "backtest_execution_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
