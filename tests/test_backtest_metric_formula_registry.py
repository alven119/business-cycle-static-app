from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_backtest_metric_formula_registry,
    summarize_backtest_metric_formula_registry,
    validate_backtest_metric_formula_registry,
)

REGISTRY_PATH = Path("specs/portfolio/backtest_metric_formula_registry.yaml")
REQUIRED_METRICS = {
    "total_return",
    "annualized_return",
    "volatility",
    "max_drawdown",
    "turnover",
    "whipsaw_count",
    "false_de_risk_cost",
    "false_re_risk_cost",
    "missed_recovery_cost",
    "late_exit_cost",
    "late_reentry_cost",
}


def test_backtest_metric_formula_registry_yaml_can_be_loaded() -> None:
    registry = load_backtest_metric_formula_registry(REGISTRY_PATH)

    assert registry.version == 1
    assert registry.status == "draft"
    validate_backtest_metric_formula_registry(registry)


def test_backtest_metric_formula_registry_summary_blocks_computation() -> None:
    registry = load_backtest_metric_formula_registry(REGISTRY_PATH)
    summary = summarize_backtest_metric_formula_registry(registry)

    assert summary["metric_count"] == 11
    assert summary["prohibited_metric_output_count"] == 11
    assert summary["compute_metric_values_allowed"] is False
    assert summary["execute_backtest_allowed"] is False
    assert summary["produce_backtest_results_allowed"] is False
    assert summary["write_data_backtests_output_allowed"] is False
    assert summary["write_public_output_allowed"] is False
    assert summary["produce_allocation_allowed"] is False
    assert summary["produce_trade_signal_allowed"] is False
    assert summary["all_metric_compute_allowed_now"] is False
    assert summary["phase_9a2_closure_status"] == "formula_registry_design_only"
    assert summary["recommended_next_phase"] == "9A3"


def test_backtest_metric_formula_registry_defines_required_metrics_as_formula_only() -> None:
    registry = load_backtest_metric_formula_registry(REGISTRY_PATH)

    assert REQUIRED_METRICS == set(registry.metric_definitions)
    for metric in registry.metric_definitions.values():
        assert {
            "category",
            "formula_text",
            "required_inputs",
            "output_unit",
            "higher_is_better",
            "allowed_in_future_results",
            "compute_allowed_now",
        }.issubset(metric)
        assert metric["compute_allowed_now"] is False


def test_backtest_metric_formula_registry_prohibits_unsafe_result_fields() -> None:
    registry = load_backtest_metric_formula_registry(REGISTRY_PATH)

    assert {
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
        "public_dashboard_output",
        "current_phase_override",
        "decision_status_override",
    }.issubset(set(registry.prohibited_result_fields))


def test_backtest_metric_formula_registry_required_caveats_are_defined() -> None:
    registry = load_backtest_metric_formula_registry(REGISTRY_PATH)

    assert {
        "metric formula registry，不是回測結果。",
        "本階段不計算任何實際績效值。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }.issubset(set(registry.required_metric_caveats_zh))
