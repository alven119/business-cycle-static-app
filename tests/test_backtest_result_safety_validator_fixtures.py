from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.portfolio import (
    BacktestResultSafetyValidatorContractError,
    load_backtest_result_safety_validator_contract,
    load_backtest_result_safety_validator_fixtures,
    validate_backtest_result_fixture,
    validate_backtest_result_safety_validator_fixtures,
)

CONTRACT_PATH = Path("specs/portfolio/backtest_result_safety_validator_contract.yaml")
FIXTURES_PATH = Path("specs/portfolio/backtest_result_safety_validator_fixtures.yaml")


def _load_contract_and_fixtures():
    contract = load_backtest_result_safety_validator_contract(CONTRACT_PATH)
    fixtures = load_backtest_result_safety_validator_fixtures(FIXTURES_PATH)
    return contract, fixtures


def _invalid_result_by_id(fixture_id: str) -> dict:
    _contract, fixtures = _load_contract_and_fixtures()
    for fixture in fixtures.invalid_result_fixtures:
        if fixture["fixture_id"] == fixture_id:
            return fixture["result"]
    raise AssertionError(f"missing invalid fixture: {fixture_id}")


def test_backtest_result_safety_validator_fixtures_yaml_can_be_loaded() -> None:
    _contract, fixtures = _load_contract_and_fixtures()

    assert fixtures.version == 1
    assert fixtures.status == "draft"
    assert len(fixtures.valid_result_fixtures) >= 3
    assert len(fixtures.invalid_result_fixtures) >= 10


def test_all_valid_and_invalid_fixtures_have_expected_validation_results() -> None:
    contract, fixtures = _load_contract_and_fixtures()
    summary = validate_backtest_result_safety_validator_fixtures(fixtures, contract)

    assert summary.valid_result_fixture_count >= 3
    assert summary.invalid_result_fixture_count >= 10
    assert summary.valid_pass_count == summary.valid_result_fixture_count
    assert summary.invalid_rejected_count == summary.invalid_result_fixture_count
    assert summary.unexpected_valid_failures == 0
    assert summary.unexpected_invalid_passes == 0
    assert summary.expected_error_mismatches == 0
    assert summary.public_output_written is False
    assert summary.data_backtests_output_written is False
    assert summary.output_written is False
    assert summary.allocation_output_generated is False
    assert summary.trade_signal_generated is False
    assert summary.result == "passed"


@pytest.mark.parametrize(
    ("fixture_id", "expected"),
    [
        ("invalid_live_allocation_field", "live_allocation"),
        ("invalid_target_weight_field", "target_weight"),
        ("invalid_buy_signal_field", "buy_signal"),
        ("invalid_sell_signal_field", "sell_signal"),
        (
            "invalid_current_market_recommendation_field",
            "current_market_recommendation",
        ),
        ("invalid_public_dashboard_output_field", "public_dashboard_output"),
        ("invalid_current_phase_override_field", "current_phase_override"),
        ("invalid_prohibited_text_buy_signal", "買進訊號"),
        ("invalid_prohibited_text_current_recommendation", "目前建議"),
        ("invalid_missing_not_investment_advice_caveat", "不構成投資建議"),
        ("invalid_missing_backtest_only_caveat", "backtest-only"),
        ("invalid_caveats_not_visible_before_metrics", "caveats_visible_before_metrics"),
        ("invalid_public_output_written_true", "public_output_written"),
        (
            "invalid_data_backtests_output_written_true",
            "data_backtests_output_written",
        ),
    ],
)
def test_invalid_fixtures_are_rejected(fixture_id: str, expected: str) -> None:
    contract, _fixtures = _load_contract_and_fixtures()
    result = _invalid_result_by_id(fixture_id)

    with pytest.raises(BacktestResultSafetyValidatorContractError, match=expected):
        validate_backtest_result_fixture(result, contract)


def test_valid_fixtures_do_not_create_output_directories() -> None:
    contract, fixtures = _load_contract_and_fixtures()

    for fixture in fixtures.valid_result_fixtures:
        validate_backtest_result_fixture(fixture["result"], contract)

    assert not Path("data/backtests/research").exists()
