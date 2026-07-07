from __future__ import annotations

import subprocess
import sys

from business_cycle.render.portfolio_policy_replay_research_surface import (
    build_portfolio_policy_replay_research_surface_view_model,
    load_portfolio_policy_replay_research_surface_contract,
    summarize_portfolio_policy_replay_research_surface,
)


def test_phase88_portfolio_policy_replay_research_surface_passes() -> None:
    summary = summarize_portfolio_policy_replay_research_surface()

    assert summary["result"] == "passed"
    assert summary["portfolio_policy_replay_research_surface_ready"] is True
    assert summary["template_catalog_ready"] is True
    assert summary["replay_schedule_matrix_ready"] is True
    assert summary["cost_turnover_assumption_panel_ready"] is True
    assert summary["scenario_policy_coverage_ready"] is True
    assert summary["policy_template_count"] == 8
    assert summary["replay_schedule_row_count"] == 8
    assert summary["scenario_count"] == 5
    assert summary["scenario_policy_coverage_row_count"] == 40
    assert summary["research_allocation_template_allowed"] is True
    assert summary["research_allocation_template_count"] == 8
    assert summary["cost_assumption_visible_count"] == 8
    assert summary["turnover_status_visible_count"] == 8
    assert summary["renderer_caveat_count"] == 6
    assert summary["policy_replay_execution_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["metric_value_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["personalized_trade_instruction_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_phase88_view_model_has_template_cost_and_scenario_rows() -> None:
    view_model = build_portfolio_policy_replay_research_surface_view_model()

    assert view_model["view_id"] == "portfolio_policy_replay_research_surface"
    assert view_model["research_only"] is True
    assert len(view_model["template_catalog_rows"]) == 8
    assert view_model["research_allocation_template_allowed"] is True
    assert view_model["research_allocation_template_count"] == 8
    assert len(view_model["replay_schedule_matrix_rows"]) == 8
    assert len(view_model["cost_turnover_assumption_rows"]) == 8
    assert len(view_model["scenario_policy_coverage_rows"]) == 40
    assert all(
        row["turnover_status"] == "not_computed_research_surface_only"
        for row in view_model["cost_turnover_assumption_rows"]
    )
    assert all(
        row["execution_allowed_now"] is False
        for row in view_model["scenario_policy_coverage_rows"]
    )


def test_phase88_contract_disables_execution_and_current_allocation() -> None:
    contract = load_portfolio_policy_replay_research_surface_contract()

    assert contract["output_policy"]["output_mode"] == "research_only_dashboard_surface"
    assert contract["output_policy"]["policy_replay_execution_allowed"] is False
    assert contract["output_policy"]["backtest_execution_allowed"] is False
    assert (
        contract["output_policy"]["current_allocation_recommendation_allowed"]
        is False
    )
    assert contract["output_policy"]["research_allocation_template_display_allowed"] is True
    assert contract["output_policy"]["personalized_trade_instruction_allowed"] is False
    assert all(value is False for value in contract["disabled_runtime_guards"].values())


def test_show_portfolio_policy_replay_research_surface_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_portfolio_policy_replay_research_surface.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "portfolio_policy_replay_research_surface_ready=true" in completed.stdout
    assert "scenario_policy_coverage_row_count=40" in completed.stdout
    assert "metric_value_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
