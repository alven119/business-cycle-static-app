from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase89a_portfolio_policy_wording_alignment_closure import (
    summarize_phase89a_portfolio_policy_wording_alignment_closure,
)


def test_phase89a_portfolio_policy_wording_alignment_closure_passes() -> None:
    summary = summarize_phase89a_portfolio_policy_wording_alignment_closure()

    assert summary["result"] == "passed"
    assert summary["phase89a_closure_ready"] is True
    assert summary["portfolio_policy_wording_alignment_ready"] is True
    assert summary["research_allocation_template_allowed"] is True
    assert summary["research_allocation_template_count"] == 8
    assert summary["dashboard_research_allocation_template_count"] == 8
    assert summary["personalized_trade_instruction_prohibited"] is True
    assert summary["personalized_trade_instruction_count"] == 0
    assert summary["live_allocation_instruction_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["policy_replay_execution_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["metric_value_count"] == 0
    assert summary["prohibited_action_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["development_next_phase"] == 89


def test_show_phase89a_portfolio_policy_wording_alignment_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase89a_portfolio_policy_wording_alignment_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase89a_closure_ready=true" in completed.stdout
    assert "research_allocation_template_allowed=true" in completed.stdout
    assert "dashboard_research_allocation_template_count=8" in completed.stdout
    assert (
        "phase89a_closure_status="
        "closed_portfolio_policy_wording_aligned_research_templates_allowed_no_personalized_trade_instruction"
        in completed.stdout
    )
    assert "result=passed" in completed.stdout
