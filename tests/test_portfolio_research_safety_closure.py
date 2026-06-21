from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_portfolio_research_safety_closure,
    summarize_portfolio_research_safety_closure,
    validate_portfolio_research_safety_closure,
)

CLOSURE_PATH = Path("specs/portfolio/portfolio_research_safety_closure.yaml")


def test_portfolio_research_safety_closure_yaml_can_be_loaded() -> None:
    closure = load_portfolio_research_safety_closure(CLOSURE_PATH)

    assert closure.version == 1
    assert closure.status == "draft"
    validate_portfolio_research_safety_closure(closure)


def test_portfolio_research_safety_closure_summary_blocks_real_backtest() -> None:
    closure = load_portfolio_research_safety_closure(CLOSURE_PATH)
    summary = summarize_portfolio_research_safety_closure(closure)

    assert summary["artifact_count"] >= 8
    assert summary["validator_count"] >= 8
    assert summary["active_blocker_count"] > 0
    assert summary["phase_8_closure_status"] == "ready_to_close_research_only"
    assert summary["research_only"] is True
    assert summary["structural_dry_run_only"] is True
    assert summary["formal_backtest_executed"] is False
    assert summary["performance_metrics_computed"] is False
    assert summary["allocation_output_generated"] is False
    assert summary["trade_signal_generated"] is False
    assert summary["data_backtests_output_written"] is False
    assert summary["public_output_written"] is False
    assert summary["live_recommendation_allowed"] is False
    assert summary["recommended_next_phase"] == "8I"


def test_portfolio_research_safety_closure_required_targets_are_defined() -> None:
    closure = load_portfolio_research_safety_closure(CLOSURE_PATH)
    target_ids = {
        target["target_id"] for target in closure.required_before_real_backtest_prototype
    }

    assert {
        "real_backtest_engine_contract_defined",
        "result_output_contract_defined",
        "metric_formula_registry_defined",
        "no_live_allocation_result_validator_defined",
        "backtest_result_caveat_required",
        "output_location_policy_defined",
    }.issubset(target_ids)


def test_portfolio_research_safety_closure_caveats_include_no_investment_advice() -> None:
    closure = load_portfolio_research_safety_closure(CLOSURE_PATH)

    assert any("不構成投資建議" in caveat for caveat in closure.caveats_zh)
