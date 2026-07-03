from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase76_portfolio_policy_template_fixtures_closure import (
    summarize_phase76_portfolio_policy_template_fixtures_closure,
)


def test_phase76_portfolio_policy_template_fixtures_closure_passes() -> None:
    summary = summarize_phase76_portfolio_policy_template_fixtures_closure()

    assert summary["result"] == "passed"
    assert summary["phase76_portfolio_policy_template_fixtures_ready"] is True
    assert summary["required_policy_template_count"] == 8
    assert summary["valid_policy_template_fixture_count"] == 8
    assert summary["valid_policy_template_pass_count"] == 8
    assert summary["invalid_policy_template_fixture_count"] == 13
    assert summary["invalid_policy_template_rejected_count"] == 13
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["live_allocation_output_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["portfolio_policy_replay_execution_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert (
        summary["phase76_closure_status"]
        == "closed_book_benchmark_portfolio_templates_fixture_validated_no_advice"
    )


def test_phase76_portfolio_policy_template_fixtures_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase76_portfolio_policy_template_fixtures_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase76_portfolio_policy_template_fixtures_ready=true" in result.stdout
    assert "required_policy_template_count=8" in result.stdout
    assert "backtest_execution_count=0" in result.stdout
