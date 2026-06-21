from __future__ import annotations

from pathlib import Path

import yaml

BENCHMARK_PATH = Path("specs/portfolio/book_strategy_golden_benchmark.yaml")


def test_book_strategy_golden_benchmark_defines_required_strategies() -> None:
    benchmark = yaml.safe_load(BENCHMARK_PATH.read_text(encoding="utf-8"))[
        "book_strategy_golden_benchmark"
    ]
    strategy_ids = {strategy["strategy_id"] for strategy in benchmark["strategies"]}

    assert {
        "passive_all_stock",
        "stock_cash_basic",
        "stock_cash_advanced",
        "stock_long_treasury_basic",
        "stock_long_treasury_advanced",
    }.issubset(strategy_ids)
    assert benchmark["summary"]["golden_strategy_count"] == 5


def test_book_strategy_golden_benchmark_defines_contributions_and_rebalance() -> None:
    benchmark = yaml.safe_load(BENCHMARK_PATH.read_text(encoding="utf-8"))[
        "book_strategy_golden_benchmark"
    ]

    assert benchmark["contributions"]["initial_contribution"]["amount"] == 10000
    assert benchmark["contributions"]["annual_contribution"]["amount"] == 10000
    assert benchmark["contributions"]["annual_contribution"]["timing"] == (
        "last_trading_day_of_each_year"
    )
    assert benchmark["rebalance"]["timing"] == "first_trading_day_of_each_year"


def test_book_strategy_golden_benchmark_defines_705030_and_long_treasury() -> None:
    benchmark = yaml.safe_load(BENCHMARK_PATH.read_text(encoding="utf-8"))[
        "book_strategy_golden_benchmark"
    ]

    assert benchmark["phase_exposures"]["boom_advanced"]["year_1_stock_weight"] == 0.7
    assert benchmark["phase_exposures"]["boom_advanced"]["year_2_stock_weight"] == 0.5
    assert benchmark["phase_exposures"]["boom_advanced"]["year_3_stock_weight"] == 0.3
    assert benchmark["phase_exposures"]["boom_advanced"][
        "two_year_boom_minimum_stock_weight"
    ] == 0.5
    assert benchmark["asset_definitions"]["long_treasury"]["issuer"] == "U.S. Treasury"
    assert benchmark["asset_definitions"]["long_treasury"]["maturity"] == (
        "7_years_or_longer"
    )
    assert benchmark["summary"]["book_benchmark_execution_allowed"] is False

