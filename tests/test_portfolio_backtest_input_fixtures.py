from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.portfolio import (
    PortfolioBacktestContractError,
    load_portfolio_backtest_input_contract,
    load_portfolio_backtest_input_fixtures,
    load_portfolio_backtest_scenario_mapping,
    validate_portfolio_backtest_input,
    validate_portfolio_backtest_input_fixtures,
)

CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_input_contract.yaml")
MAPPING_PATH = Path("specs/portfolio/portfolio_backtest_scenario_mapping.yaml")
FIXTURES_PATH = Path("specs/portfolio/portfolio_backtest_input_fixtures.yaml")


def test_portfolio_backtest_input_fixtures_yaml_can_be_loaded() -> None:
    fixtures = load_portfolio_backtest_input_fixtures(FIXTURES_PATH)

    assert fixtures.version == 1
    assert fixtures.status == "draft"
    assert len(fixtures.valid_inputs) > 0
    assert len(fixtures.invalid_inputs) > 0


def test_all_valid_backtest_input_fixtures_pass_validation() -> None:
    contract, mapping, fixtures = load_all()

    for fixture in fixtures.valid_inputs:
        validate_portfolio_backtest_input(fixture["input"], contract, mapping)


@pytest.mark.parametrize(
    ("fixture_id", "expected"),
    [
        ("invalid_live_allocation_field", "live_allocation"),
        ("invalid_target_weight_field", "target_weight"),
        ("invalid_buy_signal_field", "buy_signal"),
        ("invalid_sell_signal_field", "sell_signal"),
        ("invalid_public_output_allowed", "public_output_allowed"),
        ("invalid_unknown_scenario", "scenario_id"),
        ("invalid_unknown_policy_template", "policy_template_id"),
        ("invalid_rebalance_frequency", "rebalance_frequency"),
        ("invalid_missing_required_metric", "max_drawdown"),
        ("invalid_missing_not_investment_advice", "不構成投資建議"),
        ("invalid_current_recommendation_text", "目前建議"),
    ],
)
def test_invalid_backtest_input_fixtures_are_rejected(fixture_id: str, expected: str) -> None:
    contract, mapping, fixtures = load_all()
    by_id = {fixture["fixture_id"]: fixture["input"] for fixture in fixtures.invalid_inputs}

    with pytest.raises(PortfolioBacktestContractError, match=expected):
        validate_portfolio_backtest_input(by_id[fixture_id], contract, mapping)


def test_portfolio_backtest_input_fixture_batch_validation_passes() -> None:
    contract, mapping, fixtures = load_all()

    summary = validate_portfolio_backtest_input_fixtures(fixtures, contract, mapping)

    assert summary.valid_pass_count == summary.valid_input_count
    assert summary.invalid_rejected_count == summary.invalid_input_count
    assert summary.unexpected_valid_failures == []
    assert summary.unexpected_invalid_passes == []
    assert summary.expected_error_mismatches == []
    assert summary.passed


def load_all():
    contract = load_portfolio_backtest_input_contract(CONTRACT_PATH)
    mapping = load_portfolio_backtest_scenario_mapping(MAPPING_PATH)
    fixtures = load_portfolio_backtest_input_fixtures(FIXTURES_PATH)
    return contract, mapping, fixtures
