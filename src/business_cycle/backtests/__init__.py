"""Backtest scenario specs and catalog loading."""

from business_cycle.backtests.catalog import (
    get_scenario,
    load_backtest_scenario_catalog,
    load_backtest_scenarios,
)
from business_cycle.backtests.specs import (
    BacktestScenario,
    BacktestScenarioCatalog,
    BacktestScenarioError,
)
from business_cycle.backtests.runner import (
    BacktestPeriodResult,
    BacktestRunConfig,
    BacktestRunResult,
    generate_monthly_periods,
    run_backtest,
)

__all__ = [
    "BacktestPeriodResult",
    "BacktestRunConfig",
    "BacktestRunResult",
    "BacktestScenario",
    "BacktestScenarioCatalog",
    "BacktestScenarioError",
    "generate_monthly_periods",
    "get_scenario",
    "load_backtest_scenario_catalog",
    "load_backtest_scenarios",
    "run_backtest",
]
