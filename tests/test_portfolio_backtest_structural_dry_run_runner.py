from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_portfolio_backtest_dry_run_contract,
    load_portfolio_backtest_input_contract,
    load_portfolio_backtest_input_fixtures,
    load_portfolio_backtest_scenario_mapping,
    run_portfolio_backtest_structural_dry_run,
    validate_portfolio_backtest_dry_run_output,
)

DRY_RUN_CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_dry_run_contract.yaml")
INPUT_CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_input_contract.yaml")
MAPPING_PATH = Path("specs/portfolio/portfolio_backtest_scenario_mapping.yaml")
FIXTURES_PATH = Path("specs/portfolio/portfolio_backtest_input_fixtures.yaml")


def test_structural_dry_run_runner_loads_contracts_and_processes_valid_inputs() -> None:
    dry_run_contract, input_contract, mapping, fixtures = load_all()

    report = run_portfolio_backtest_structural_dry_run(
        dry_run_contract,
        input_contract,
        mapping,
        fixtures,
    )

    summary = report["summary"]
    assert summary["dry_run_count"] == len(fixtures.valid_inputs)
    assert summary["valid_dry_run_count"] == len(fixtures.valid_inputs)
    assert summary["invalid_dry_run_count"] == 0


def test_structural_dry_run_outputs_are_valid_and_safe() -> None:
    dry_run_contract, input_contract, mapping, fixtures = load_all()
    report = run_portfolio_backtest_structural_dry_run(
        dry_run_contract,
        input_contract,
        mapping,
        fixtures,
    )
    prohibited = {
        "total_return",
        "max_drawdown",
        "turnover",
        "allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
    }

    for output in report["outputs"]:
        validate_portfolio_backtest_dry_run_output(output, dry_run_contract)
        assert prohibited.isdisjoint(output)
        assert prohibited.isdisjoint(output.get("structural_summary", {}))


def test_structural_dry_run_summary_blocks_performance_output_and_actions() -> None:
    dry_run_contract, input_contract, mapping, fixtures = load_all()
    report = run_portfolio_backtest_structural_dry_run(
        dry_run_contract,
        input_contract,
        mapping,
        fixtures,
    )
    summary = report["summary"]

    assert summary["performance_metrics_computed"] is False
    assert summary["output_written"] is False
    assert summary["data_backtests_output_written"] is False
    assert summary["public_output_written"] is False
    assert summary["allocation_output_generated"] is False
    assert summary["trade_signal_generated"] is False
    assert summary["result"] == "passed"


def load_all():
    dry_run_contract = load_portfolio_backtest_dry_run_contract(DRY_RUN_CONTRACT_PATH)
    input_contract = load_portfolio_backtest_input_contract(INPUT_CONTRACT_PATH)
    mapping = load_portfolio_backtest_scenario_mapping(MAPPING_PATH)
    fixtures = load_portfolio_backtest_input_fixtures(FIXTURES_PATH)
    return dry_run_contract, input_contract, mapping, fixtures
