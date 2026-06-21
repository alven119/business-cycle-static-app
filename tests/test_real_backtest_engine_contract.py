from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_real_backtest_engine_contract,
    summarize_real_backtest_engine_contract,
    validate_real_backtest_engine_contract,
)

CONTRACT_PATH = Path("specs/portfolio/real_backtest_engine_contract.yaml")


def test_real_backtest_engine_contract_yaml_can_be_loaded() -> None:
    contract = load_real_backtest_engine_contract(CONTRACT_PATH)

    assert contract.version == 1
    assert contract.status == "draft"
    validate_real_backtest_engine_contract(contract)


def test_real_backtest_engine_contract_summary_blocks_runtime() -> None:
    contract = load_real_backtest_engine_contract(CONTRACT_PATH)
    summary = summarize_real_backtest_engine_contract(contract)

    assert summary["input_contract_count"] >= 5
    assert summary["future_dependency_contract_count"] >= 5
    assert summary["engine_stage_count"] >= 8
    assert summary["prohibited_output_count"] > 0
    assert summary["prohibited_auto_write_location_count"] > 0
    assert summary["implement_engine_runtime_allowed"] is False
    assert summary["execute_backtest_allowed"] is False
    assert summary["compute_performance_metrics_allowed"] is False
    assert summary["produce_backtest_results_allowed"] is False
    assert summary["write_data_backtests_output_allowed"] is False
    assert summary["write_public_output_allowed"] is False
    assert summary["produce_allocation_allowed"] is False
    assert summary["produce_trade_signal_allowed"] is False
    assert summary["phase_9a_closure_status"] == "contract_design_only"
    assert summary["recommended_next_phase"] == "9A1"


def test_real_backtest_engine_contract_stage_blockers_are_defined() -> None:
    contract = load_real_backtest_engine_contract(CONTRACT_PATH)
    stages = {
        stage["stage_id"]: stage
        for stage in contract.engine_stage_contract["stages"]
    }

    assert stages["compute_metrics"]["allowed_now"] == "blocked_until_metric_registry"
    assert (
        stages["build_result_output"]["allowed_now"]
        == "blocked_until_result_output_contract"
    )
    assert (
        stages["write_research_output"]["allowed_now"]
        == "blocked_until_output_location_policy"
    )


def test_real_backtest_engine_contract_future_dependencies_are_required() -> None:
    contract = load_real_backtest_engine_contract(CONTRACT_PATH)

    assert {
        "metric_formula_registry",
        "backtest_result_output_contract",
        "backtest_result_safety_validator",
        "output_location_policy",
        "result_caveat_policy",
    }.issubset(contract.required_future_dependency_contracts)


def test_real_backtest_engine_contract_prohibits_unsafe_outputs_and_locations() -> None:
    contract = load_real_backtest_engine_contract(CONTRACT_PATH)

    assert {
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
        "public_dashboard_output",
    }.issubset(set(contract.prohibited_engine_outputs))
    assert {"public", "dashboard", "github_pages", "data/backtests"}.issubset(
        set(contract.prohibited_auto_write_locations)
    )


def test_real_backtest_engine_contract_caveats_include_no_investment_advice() -> None:
    contract = load_real_backtest_engine_contract(CONTRACT_PATH)

    assert any("不構成投資建議" in caveat for caveat in contract.caveats_zh)
