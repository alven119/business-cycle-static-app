from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.portfolio import (
    PortfolioPolicyTemplateError,
    REQUIRED_TEMPLATE_IDS,
    load_portfolio_policy_template_fixtures,
    load_portfolio_policy_template_schema,
    validate_portfolio_policy_template,
    validate_portfolio_policy_template_fixtures,
)

SCHEMA_PATH = Path("specs/portfolio/portfolio_policy_template_schema.yaml")
FIXTURES_PATH = Path("specs/portfolio/portfolio_policy_template_fixtures.yaml")


def test_portfolio_policy_template_schema_loads() -> None:
    schema = load_portfolio_policy_template_schema(SCHEMA_PATH)

    assert schema.version == 1
    assert schema.status == "draft"


def test_portfolio_policy_template_schema_has_allowed_templates_and_prohibited_fields() -> None:
    schema = load_portfolio_policy_template_schema(SCHEMA_PATH)

    assert set(schema.allowed_template_ids) == REQUIRED_TEMPLATE_IDS
    assert len(schema.allowed_template_ids) == 8
    assert {"target_weight", "buy_signal", "sell_signal", "current_market_recommendation"}.issubset(
        schema.prohibited_fields
    )
    assert schema.recommended_next_phase["phase_id"] == "77"


def test_valid_policy_template_fixtures_pass() -> None:
    schema = load_portfolio_policy_template_schema(SCHEMA_PATH)
    fixtures = load_portfolio_policy_template_fixtures(FIXTURES_PATH)
    by_id = {fixture["fixture_id"]: fixture["template"] for fixture in fixtures.valid_templates}

    assert set(template["template_id"] for template in by_id.values()) == REQUIRED_TEMPLATE_IDS
    for template in by_id.values():
        validate_portfolio_policy_template(template, schema)


@pytest.mark.parametrize(
    ("fixture_id", "expected"),
    [
        ("invalid_live_allocation_allowed", "live_allocation_allowed"),
        ("invalid_trade_signal_allowed", "trade_signal_allowed"),
        ("invalid_target_weight_field", "target_weight"),
        ("invalid_buy_signal_field", "buy_signal"),
        ("invalid_sell_signal_field", "sell_signal"),
        ("invalid_current_market_recommendation_field", "current_market_recommendation"),
        ("invalid_prohibited_text_current_recommendation", "目前建議"),
        ("invalid_prohibited_text_buy_recommendation", "建議買進"),
        ("invalid_prohibited_text_sell_recommendation", "建議賣出"),
        ("invalid_prohibited_text_add_risk", "加碼"),
        ("invalid_prohibited_text_reduce_risk", "減碼"),
        ("invalid_missing_not_investment_advice_caveat", "不構成投資建議"),
        ("invalid_boom_missing_705030", "stock_weight_levels_for_backtest_only"),
    ],
)
def test_invalid_policy_template_fixtures_are_rejected(fixture_id: str, expected: str) -> None:
    schema = load_portfolio_policy_template_schema(SCHEMA_PATH)
    fixtures = load_portfolio_policy_template_fixtures(FIXTURES_PATH)
    by_id = {fixture["fixture_id"]: fixture["template"] for fixture in fixtures.invalid_templates}

    with pytest.raises(PortfolioPolicyTemplateError, match=expected):
        validate_portfolio_policy_template(by_id[fixture_id], schema)


def test_policy_template_fixture_batch_validation_passes() -> None:
    schema = load_portfolio_policy_template_schema(SCHEMA_PATH)
    fixtures = load_portfolio_policy_template_fixtures(FIXTURES_PATH)

    summary = validate_portfolio_policy_template_fixtures(fixtures, schema)

    assert summary.valid_pass_count == summary.valid_template_count
    assert summary.invalid_rejected_count == summary.invalid_template_count
    assert summary.unexpected_valid_failures == []
    assert summary.unexpected_invalid_passes == []
    assert summary.expected_error_mismatches == []
    assert summary.passed
