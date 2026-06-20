from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_portfolio_backtest_dry_run_contract,
    summarize_portfolio_backtest_dry_run_contract,
    validate_portfolio_backtest_dry_run_contract,
)

CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_dry_run_contract.yaml")


def test_portfolio_backtest_dry_run_contract_yaml_can_be_loaded() -> None:
    contract = load_portfolio_backtest_dry_run_contract(CONTRACT_PATH)

    assert contract.version == 1
    assert contract.status == "draft"
    validate_portfolio_backtest_dry_run_contract(contract)


def test_portfolio_backtest_dry_run_scope_disallows_real_backtest_outputs() -> None:
    contract = load_portfolio_backtest_dry_run_contract(CONTRACT_PATH)
    disallowed = contract.dry_run_scope["disallowed"]

    assert disallowed["compute_returns"] is True
    assert disallowed["compute_live_allocation"] is True
    assert disallowed["produce_trade_signal"] is True
    assert disallowed["write_data_backtests_output"] is True
    assert disallowed["write_public_output"] is True


def test_portfolio_backtest_dry_run_output_schema_blocks_performance_and_actions() -> None:
    contract = load_portfolio_backtest_dry_run_contract(CONTRACT_PATH)
    prohibited = set(contract.dry_run_output_schema["prohibited_fields"])

    assert {
        "total_return",
        "max_drawdown",
        "turnover",
        "allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "public_dashboard_output",
    }.issubset(prohibited)


def test_portfolio_backtest_dry_run_stdout_contract_has_required_false_lines() -> None:
    contract = load_portfolio_backtest_dry_run_contract(CONTRACT_PATH)
    required_lines = set(contract.stdout_contract["required_lines"])

    assert {
        "output_written=false",
        "data_backtests_output_written=false",
        "public_output_written=false",
        "allocation_output_generated=false",
        "trade_signal_generated=false",
        "result=passed",
    }.issubset(required_lines)


def test_portfolio_backtest_dry_run_stdout_blocks_trade_signal_text() -> None:
    contract = load_portfolio_backtest_dry_run_contract(CONTRACT_PATH)
    patterns = {
        pattern
        for values in contract.stdout_contract["prohibited_text_patterns"].values()
        for pattern in values
    }

    assert {"買進訊號", "賣出訊號", "buy signal", "sell signal"}.issubset(patterns)


def test_portfolio_backtest_dry_run_summary_recommends_8f_and_blocks_outputs() -> None:
    contract = load_portfolio_backtest_dry_run_contract(CONTRACT_PATH)
    summary = summarize_portfolio_backtest_dry_run_contract(contract)

    assert summary["compute_returns_allowed"] is False
    assert summary["allocation_output_allowed"] is False
    assert summary["trade_signal_output_allowed"] is False
    assert summary["data_backtests_output_allowed"] is False
    assert summary["public_output_allowed"] is False
    assert summary["recommended_next_phase"] == "8F"


def test_portfolio_backtest_dry_run_caveats_include_no_investment_advice() -> None:
    contract = load_portfolio_backtest_dry_run_contract(CONTRACT_PATH)

    assert any("不構成投資建議" in caveat for caveat in contract.caveats_zh)
