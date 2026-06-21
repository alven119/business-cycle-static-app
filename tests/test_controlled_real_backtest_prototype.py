from __future__ import annotations

from pathlib import Path
from typing import Any

from business_cycle.portfolio import (
    load_controlled_real_backtest_prototype_fixtures,
    run_controlled_backtest_case,
    run_controlled_real_backtest_prototype,
    summarize_controlled_real_backtest_prototype,
    validate_controlled_prototype_fixtures,
)

FIXTURES_PATH = Path("specs/portfolio/controlled_real_backtest_prototype_fixtures.yaml")


def test_controlled_real_backtest_prototype_fixtures_yaml_can_be_loaded() -> None:
    fixtures = load_controlled_real_backtest_prototype_fixtures(FIXTURES_PATH)

    assert fixtures.version == 1
    assert fixtures.status == "experimental"
    assert len(fixtures.prototype_cases) >= 2
    validate_controlled_prototype_fixtures(fixtures)


def test_controlled_real_backtest_prototype_cases_are_fixture_only() -> None:
    fixtures = load_controlled_real_backtest_prototype_fixtures(FIXTURES_PATH)

    for case in fixtures.prototype_cases:
        behavior = case["expected_behavior"]
        assert case["data_mode"] == "controlled_fixture_only"
        assert case["backtest_only"] is True
        assert behavior["output_write_allowed"] is False
        assert behavior["public_output_allowed"] is False
        assert behavior["allocation_output_allowed"] is False
        assert behavior["trade_signal_allowed"] is False


def test_run_controlled_backtest_case_computes_required_metrics_in_memory() -> None:
    fixtures = load_controlled_real_backtest_prototype_fixtures(FIXTURES_PATH)
    case_result = run_controlled_backtest_case(fixtures.prototype_cases[0])

    assert {
        "total_return",
        "annualized_return",
        "volatility",
        "max_drawdown",
        "turnover",
    }.issubset(case_result.metrics)
    assert case_result.portfolio_value_path
    assert case_result.portfolio_returns


def test_controlled_real_backtest_prototype_summary_flags_are_safe() -> None:
    fixtures = load_controlled_real_backtest_prototype_fixtures(FIXTURES_PATH)
    run_result = run_controlled_real_backtest_prototype(fixtures)
    summary = summarize_controlled_real_backtest_prototype(run_result)

    assert summary["case_count"] >= 2
    assert summary["prototype_run_count"] == summary["case_count"]
    assert summary["computed_metric_count"] >= 5
    assert summary["in_memory_only"] is True
    assert summary["controlled_metric_computation_allowed"] is True
    assert summary["result_file_written"] is False
    assert summary["data_backtests_output_written"] is False
    assert summary["public_output_written"] is False
    assert summary["output_directory_created"] is False
    assert summary["allocation_output_generated"] is False
    assert summary["trade_signal_generated"] is False
    assert summary["live_recommendation_generated"] is False
    assert summary["dashboard_integration"] is False
    assert summary["result"] == "passed"
    assert summary["recommended_next_phase"] == "9B1"


def test_controlled_real_backtest_prototype_fixtures_do_not_contain_prohibited_content() -> None:
    fixtures = load_controlled_real_backtest_prototype_fixtures(FIXTURES_PATH)
    prohibited_text = (
        "目前建議",
        "建議買進",
        "建議賣出",
        "買進訊號",
        "賣出訊號",
        "target weight",
        "buy signal",
        "sell signal",
        "investment advice",
    )

    for case in fixtures.prototype_cases:
        for path, value in _walk_nested(case):
            if path and path[-1] in fixtures.prohibited_fixture_fields:
                raise AssertionError(f"prohibited fixture field present: {path[-1]}")
            if isinstance(value, str):
                for field in fixtures.prohibited_fixture_fields:
                    assert field not in value
                for text in prohibited_text:
                    assert text not in value


def test_controlled_real_backtest_prototype_does_not_create_outputs() -> None:
    load_controlled_real_backtest_prototype_fixtures(FIXTURES_PATH)

    assert not Path("data/backtests/research").exists()


def _walk_nested(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    items = [(path, value)]
    if isinstance(value, dict):
        for key, nested in value.items():
            items.extend(_walk_nested(nested, (*path, str(key))))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            items.extend(_walk_nested(nested, (*path, str(index))))
    return items
