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
from business_cycle.backtests.book_gap import (
    BookIndicatorGapAnalysis,
    BookIndicatorGapAnalysisError,
    high_priority_count as high_priority_book_gap_count,
    load_book_indicator_gap_analysis,
    sensitivity_issues,
    validate_book_indicator_gap_analysis,
)
from business_cycle.backtests.breadth_sensitivity import (
    BreadthSensitivityError,
    BreadthSensitivityMatrix,
    build_breadth_sensitivity_summary,
    load_breadth_sensitivity_matrix,
    run_breadth_sensitivity_experiment,
    validate_breadth_sensitivity_matrix,
    write_breadth_sensitivity_summary,
)
from business_cycle.backtests.calibration import (
    CalibrationPlan,
    CalibrationPlanError,
    load_calibration_plan,
    validate_calibration_plan,
)
from business_cycle.backtests.calibration_experiment import (
    CalibrationExperimentError,
    build_calibration_experiment_summary,
    run_calibration_experiment,
)
from business_cycle.backtests.calibration_review import (
    CalibrationReviewError,
    build_calibration_acceptance_review,
    write_calibration_acceptance_review,
)
from business_cycle.backtests.covid_false_positive import (
    CovidFalsePositiveError,
    build_covid_false_positive_diagnostic,
    write_covid_false_positive_diagnostic,
)
from business_cycle.backtests.full_horizon_calibration import (
    run_full_horizon_calibration,
    write_full_horizon_calibration_outputs,
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
    "BookIndicatorGapAnalysis",
    "BookIndicatorGapAnalysisError",
    "BreadthSensitivityError",
    "BreadthSensitivityMatrix",
    "CalibrationPlan",
    "CalibrationPlanError",
    "CalibrationExperimentError",
    "CalibrationReviewError",
    "CovidFalsePositiveError",
    "attribution_quality_counts",
    "build_attribution_smoke_summary",
    "build_backtest_smoke_summary",
    "build_backtest_report",
    "build_calibration_experiment_summary",
    "build_calibration_acceptance_review",
    "build_covid_false_positive_diagnostic",
    "build_breadth_sensitivity_summary",
    "build_transition_attribution",
    "generate_monthly_periods",
    "get_scenario",
    "high_priority_book_gap_count",
    "load_book_indicator_gap_analysis",
    "load_breadth_sensitivity_matrix",
    "load_calibration_plan",
    "load_backtest_scenario_catalog",
    "load_backtest_scenarios",
    "run_attribution_smoke",
    "run_backtest",
    "run_backtest_smoke",
    "run_calibration_experiment",
    "run_full_horizon_calibration",
    "run_breadth_sensitivity_experiment",
    "sensitivity_issues",
    "write_transition_attribution",
    "write_calibration_acceptance_review",
    "write_covid_false_positive_diagnostic",
    "write_full_horizon_calibration_outputs",
    "validate_calibration_plan",
    "validate_book_indicator_gap_analysis",
    "validate_breadth_sensitivity_matrix",
    "write_backtest_report",
    "write_breadth_sensitivity_summary",
]
