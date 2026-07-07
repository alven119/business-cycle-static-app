from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase88_portfolio_policy_replay_research_surface_closure import (
    summarize_phase88_portfolio_policy_replay_research_surface_closure,
)


def test_phase88_portfolio_policy_replay_research_surface_closure_passes() -> None:
    summary = summarize_phase88_portfolio_policy_replay_research_surface_closure()

    assert summary["result"] == "passed"
    assert summary["phase88_closure_ready"] is True
    assert summary["portfolio_policy_replay_research_surface_ready"] is True
    assert summary["portfolio_replay_dashboard_page_ready"] is True
    assert summary["dashboard_policy_surface_view_ready"] is True
    assert summary["rendered_policy_surface_ready"] is True
    assert summary["html_policy_template_count"] == 8
    assert summary["html_replay_schedule_row_count"] == 8
    assert summary["html_scenario_policy_coverage_row_count"] == 40
    assert summary["research_allocation_template_allowed"] is True
    assert summary["research_allocation_template_count"] == 8
    assert summary["html_research_allocation_template_count"] == 8
    assert summary["html_cost_assumption_row_count"] == 8
    assert summary["html_renderer_caveat_count"] == 6
    assert summary["policy_replay_execution_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["metric_value_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["personalized_trade_instruction_count"] == 0
    assert summary["prohibited_action_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["development_next_phase"] == 89


def test_show_phase88_portfolio_policy_replay_research_surface_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase88_portfolio_policy_replay_research_surface_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase88_closure_ready=true" in completed.stdout
    assert "html_policy_template_count=8" in completed.stdout
    assert "html_research_allocation_template_count=8" in completed.stdout
    assert (
        "phase88_closure_status="
        "closed_portfolio_policy_replay_research_surface_ready_no_execution_or_advice"
        in completed.stdout
    )
    assert "result=passed" in completed.stdout
