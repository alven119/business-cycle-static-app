from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_portfolio_policy_research_plan,
    summarize_portfolio_policy_research_plan,
    validate_portfolio_policy_research_plan,
)

PLAN_PATH = Path("specs/portfolio/portfolio_policy_research_plan.yaml")


def test_portfolio_policy_research_plan_yaml_can_be_loaded() -> None:
    plan = load_portfolio_policy_research_plan(PLAN_PATH)

    assert plan.version == 1
    assert plan.status == "draft"
    validate_portfolio_policy_research_plan(plan)


def test_portfolio_policy_research_plan_has_three_templates() -> None:
    plan = load_portfolio_policy_research_plan(PLAN_PATH)
    summary = summarize_portfolio_policy_research_plan(plan)

    assert summary["template_count"] == 3
    assert set(plan.research_policy_templates) == {
        "boom_de_risking_template",
        "recession_defense_template",
        "recovery_re_risking_template",
    }


def test_portfolio_policy_research_plan_boom_template_has_backtest_only_70_50_30() -> None:
    plan = load_portfolio_policy_research_plan(PLAN_PATH)
    params = plan.research_policy_templates["boom_de_risking_template"]["book_aligned_parameters"]

    assert params["stock_weight_levels_for_backtest_only"] == [0.70, 0.50, 0.30]
    assert params["short_boom_min_stock_weight_for_backtest_only"] == 0.50
    assert params["extended_boom_year_4_stock_weight_for_backtest_only"] == 0.30


def test_portfolio_policy_research_plan_disallows_live_recommendations_and_output() -> None:
    plan = load_portfolio_policy_research_plan(PLAN_PATH)
    disallowed = plan.policy_scope["disallowed_now"]

    assert disallowed["live_allocation_output"] is True
    assert disallowed["current_market_recommendation"] is True
    assert disallowed["trade_signal_generation"] is True
    assert disallowed["public_output"] is True


def test_portfolio_policy_research_plan_metrics_include_required_risk_costs() -> None:
    plan = load_portfolio_policy_research_plan(PLAN_PATH)
    metrics = set(plan.required_backtest_dimensions["metrics"])

    assert {"max_drawdown", "turnover", "false_de_risk_cost", "false_re_risk_cost"}.issubset(
        metrics
    )


def test_portfolio_policy_research_plan_acceptance_targets_include_safety_gates() -> None:
    plan = load_portfolio_policy_research_plan(PLAN_PATH)
    target_ids = {
        target["target_id"]
        for target in plan.required_acceptance_before_policy_backtest
    }

    assert "no_live_allocation_output" in target_ids
    assert "no_trade_signal_language" in target_ids
    assert "not_investment_advice_caveat" in target_ids


def test_portfolio_policy_research_plan_recommends_8b() -> None:
    plan = load_portfolio_policy_research_plan(PLAN_PATH)

    assert plan.recommended_next_phase["phase_id"] == "8B"


def test_portfolio_policy_research_plan_contains_no_investment_advice_caveat() -> None:
    plan = load_portfolio_policy_research_plan(PLAN_PATH)

    assert any("不構成投資建議" in caveat for caveat in plan.caveats_zh)
