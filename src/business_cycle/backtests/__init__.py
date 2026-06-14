"""Backtest scenario specs and catalog loading."""

from business_cycle.backtests.attribution import (
    attribution_quality_counts,
    build_transition_attribution,
    write_transition_attribution,
)
from business_cycle.backtests.attribution_smoke import (
    AttributionSmokeError,
    build_attribution_smoke_summary,
    run_attribution_smoke,
)
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
from business_cycle.backtests.report import build_backtest_report, write_backtest_report
from business_cycle.backtests.smoke import (
    BacktestSmokeError,
    build_backtest_smoke_summary,
    run_backtest_smoke,
)

__all__ = [
    "BacktestPeriodResult",
    "BacktestRunConfig",
    "BacktestRunResult",
    "BacktestScenario",
    "BacktestScenarioCatalog",
    "BacktestScenarioError",
    "BacktestSmokeError",
    "AttributionSmokeError",
    "attribution_quality_counts",
    "build_attribution_smoke_summary",
    "build_backtest_smoke_summary",
    "build_backtest_report",
    "build_transition_attribution",
    "generate_monthly_periods",
    "get_scenario",
    "load_backtest_scenario_catalog",
    "load_backtest_scenarios",
    "run_attribution_smoke",
    "run_backtest",
    "run_backtest_smoke",
    "write_transition_attribution",
    "write_backtest_report",
]
