from __future__ import annotations

import subprocess
import sys

from business_cycle.portfolio.policy_replay_schedule import (
    build_portfolio_policy_replay_schedule_view_model,
    load_portfolio_policy_replay_schedule_contract,
    summarize_portfolio_policy_replay_schedule,
)


def test_phase77_portfolio_policy_replay_schedule_passes() -> None:
    summary = summarize_portfolio_policy_replay_schedule()

    assert summary["result"] == "passed"
    assert summary["portfolio_policy_replay_schedule_contract_ready"] is True
    assert summary["schedule_row_count"] == 8
    assert summary["template_with_schedule_count"] == 8
    assert summary["missing_template_schedule_count"] == 0
    assert summary["invalid_template_reference_count"] == 0
    assert summary["execution_allowed_now_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["portfolio_policy_replay_execution_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["live_allocation_output_count"] == 0
    assert summary["prohibited_schedule_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_phase77_schedule_keeps_policy_replay_research_only() -> None:
    contract = load_portfolio_policy_replay_schedule_contract()

    assert contract.output_policy["output_mode"] == "research_schedule_only"
    assert contract.output_policy["execution_allowed_now"] is False
    assert contract.output_policy["backtest_execution_allowed"] is False
    assert contract.output_policy["current_allocation_recommendation_allowed"] is False
    assert contract.output_policy["trade_signal_allowed"] is False
    assert contract.output_policy["live_allocation_allowed"] is False
    for row in contract.schedule_rows:
        assert row["execution_allowed_now"] is False
        assert row["backtest_execution_allowed"] is False
        assert row["current_allocation_recommendation_allowed"] is False
        assert row["trade_signal_allowed"] is False
        assert row["live_allocation_allowed"] is False
        assert row["allowed_state_inputs"]
        assert row["caveats_zh"]
        assert "research" in row["schedule_family"] or "book_boom" in row["schedule_family"]


def test_phase77_replay_schedule_view_model_is_non_executing() -> None:
    view_model = build_portfolio_policy_replay_schedule_view_model()

    assert view_model["view_id"] == "portfolio_policy_replay_schedule"
    assert view_model["research_only"] is True
    assert view_model["output_mode"] == "research_schedule_only"
    assert len(view_model["schedule_rows"]) == 8
    assert view_model["trust_metadata"]["backtest_execution_enabled"] is False
    assert view_model["trust_metadata"]["trade_signal_enabled"] is False
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False


def test_show_portfolio_policy_replay_schedule_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_portfolio_policy_replay_schedule.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "portfolio_policy_replay_schedule_contract_ready=true" in completed.stdout
    assert "schedule_row_count=8" in completed.stdout
    assert "backtest_execution_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
