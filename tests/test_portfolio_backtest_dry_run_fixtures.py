from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.portfolio import (
    PortfolioBacktestDryRunContractError,
    load_portfolio_backtest_dry_run_contract,
    load_portfolio_backtest_dry_run_fixtures,
    validate_portfolio_backtest_dry_run_fixtures,
    validate_portfolio_backtest_dry_run_output,
)

CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_dry_run_contract.yaml")
FIXTURES_PATH = Path("specs/portfolio/portfolio_backtest_dry_run_fixtures.yaml")


def test_portfolio_backtest_dry_run_fixtures_yaml_can_be_loaded() -> None:
    fixtures = load_portfolio_backtest_dry_run_fixtures(FIXTURES_PATH)

    assert fixtures.version == 1
    assert fixtures.status == "draft"
    assert len(fixtures.valid_dry_run_outputs) > 0
    assert len(fixtures.invalid_dry_run_outputs) > 0


def test_all_valid_dry_run_outputs_pass_validation() -> None:
    contract, fixtures = load_all()

    for fixture in fixtures.valid_dry_run_outputs:
        validate_portfolio_backtest_dry_run_output(fixture["output"], contract)


@pytest.mark.parametrize(
    ("fixture_id", "expected"),
    [
        ("invalid_output_total_return", "total_return"),
        ("invalid_output_max_drawdown", "max_drawdown"),
        ("invalid_output_allocation", "allocation"),
        ("invalid_output_target_weight", "target_weight"),
        ("invalid_output_buy_signal", "buy_signal"),
        ("invalid_output_public_dashboard", "public_dashboard_output"),
        ("invalid_output_written_true", "output_written"),
        ("invalid_data_backtests_output_written_true", "data_backtests_output_written"),
        ("invalid_missing_not_investment_advice", "不構成投資建議"),
        ("invalid_prohibited_text_buy_signal", "買進訊號"),
    ],
)
def test_invalid_dry_run_outputs_are_rejected(fixture_id: str, expected: str) -> None:
    contract, fixtures = load_all()
    by_id = {fixture["fixture_id"]: fixture["output"] for fixture in fixtures.invalid_dry_run_outputs}

    with pytest.raises(PortfolioBacktestDryRunContractError, match=expected):
        validate_portfolio_backtest_dry_run_output(by_id[fixture_id], contract)


def test_portfolio_backtest_dry_run_fixture_batch_validation_passes() -> None:
    contract, fixtures = load_all()

    summary = validate_portfolio_backtest_dry_run_fixtures(fixtures, contract)

    assert summary.valid_pass_count == summary.valid_output_count
    assert summary.invalid_rejected_count == summary.invalid_output_count
    assert summary.unexpected_valid_failures == []
    assert summary.unexpected_invalid_passes == []
    assert summary.expected_error_mismatches == []
    assert summary.output_written is False
    assert summary.data_backtests_output_written is False
    assert summary.public_output_written is False
    assert summary.allocation_output_generated is False
    assert summary.trade_signal_generated is False
    assert summary.passed


def load_all():
    contract = load_portfolio_backtest_dry_run_contract(CONTRACT_PATH)
    fixtures = load_portfolio_backtest_dry_run_fixtures(FIXTURES_PATH)
    return contract, fixtures
