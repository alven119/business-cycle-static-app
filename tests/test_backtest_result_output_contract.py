from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_backtest_result_output_contract,
    summarize_backtest_result_output_contract,
    validate_backtest_result_output_contract,
)

CONTRACT_PATH = Path("specs/portfolio/backtest_result_output_contract.yaml")


def test_backtest_result_output_contract_yaml_can_be_loaded() -> None:
    contract = load_backtest_result_output_contract(CONTRACT_PATH)

    assert contract.version == 1
    assert contract.status == "draft"
    validate_backtest_result_output_contract(contract)


def test_backtest_result_output_contract_summary_blocks_result_generation() -> None:
    contract = load_backtest_result_output_contract(CONTRACT_PATH)
    summary = summarize_backtest_result_output_contract(contract)

    assert summary["required_result_field_count"] > 0
    assert summary["future_metric_field_count"] >= 8
    assert summary["prohibited_result_field_count"] > 0
    assert summary["prohibited_auto_write_location_count"] > 0
    assert summary["produce_backtest_results_allowed"] is False
    assert summary["compute_metric_values_allowed"] is False
    assert summary["write_result_files_allowed"] is False
    assert summary["write_data_backtests_output_allowed"] is False
    assert summary["write_public_output_allowed"] is False
    assert summary["produce_allocation_allowed"] is False
    assert summary["produce_trade_signal_allowed"] is False
    assert summary["metric_values_allowed_now"] is False
    assert summary["auto_write_allowed_now"] is False
    assert summary["phase_9a1_closure_status"] == "result_contract_design_only"
    assert summary["recommended_next_phase"] == "9A2"


def test_backtest_result_output_contract_future_metric_fields_are_schema_only() -> None:
    contract = load_backtest_result_output_contract(CONTRACT_PATH)
    metrics = set(
        contract.result_object_schema["allowed_metric_fields_for_future_results"]
    )

    assert {
        "total_return",
        "annualized_return",
        "volatility",
        "max_drawdown",
        "turnover",
        "false_de_risk_cost",
        "false_re_risk_cost",
    }.issubset(metrics)
    assert contract.result_object_schema["metric_values_allowed_now"] is False


def test_backtest_result_output_contract_prohibits_unsafe_fields_and_locations() -> None:
    contract = load_backtest_result_output_contract(CONTRACT_PATH)

    assert {
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
        "public_dashboard_output",
        "current_phase_override",
        "decision_status_override",
    }.issubset(set(contract.prohibited_result_fields))
    assert {"public", "dashboard", "github_pages", "data/backtests"}.issubset(
        set(contract.output_location_dependency["prohibited_auto_write_locations"])
    )


def test_backtest_result_output_contract_required_caveats_are_defined() -> None:
    contract = load_backtest_result_output_contract(CONTRACT_PATH)

    assert {
        "backtest-only，不是目前配置建議。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }.issubset(set(contract.required_result_caveats_zh))
