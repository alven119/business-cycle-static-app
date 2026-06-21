from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_backtest_result_caveat_policy,
    summarize_backtest_result_caveat_policy,
    validate_backtest_result_caveat_policy,
)

POLICY_PATH = Path("specs/portfolio/backtest_result_caveat_policy.yaml")


def test_backtest_result_caveat_policy_yaml_can_be_loaded() -> None:
    policy = load_backtest_result_caveat_policy(POLICY_PATH)

    assert policy.version == 1
    assert policy.status == "draft"
    validate_backtest_result_caveat_policy(policy)


def test_backtest_result_caveat_policy_summary_blocks_result_generation() -> None:
    policy = load_backtest_result_caveat_policy(POLICY_PATH)
    summary = summarize_backtest_result_caveat_policy(policy)

    assert summary["required_global_caveat_count"] >= 4
    assert summary["contextual_caveat_count"] >= 5
    assert summary["prohibited_text_pattern_count"] > 0
    assert summary["prohibited_result_field_count"] > 0
    assert summary["future_validation_rule_count"] >= 6
    assert summary["produce_backtest_results_allowed"] is False
    assert summary["compute_metric_values_allowed"] is False
    assert summary["write_result_files_allowed"] is False
    assert summary["write_data_backtests_output_allowed"] is False
    assert summary["write_public_output_allowed"] is False
    assert summary["create_output_directories_allowed"] is False
    assert summary["produce_allocation_allowed"] is False
    assert summary["produce_trade_signal_allowed"] is False
    assert summary["caveats_visible_before_metrics"] is True
    assert summary["phase_9a4_closure_status"] == "caveat_policy_design_only"
    assert summary["recommended_next_phase"] == "9A5"


def test_backtest_result_caveat_policy_global_caveats_are_required() -> None:
    policy = load_backtest_result_caveat_policy(POLICY_PATH)

    assert {
        "backtest-only，不是目前配置建議。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }.issubset(set(policy.required_global_caveats_zh))


def test_backtest_result_caveat_policy_contextual_caveats_are_required() -> None:
    policy = load_backtest_result_caveat_policy(POLICY_PATH)

    assert {
        "revised_data",
        "transaction_cost",
        "false_signal_cost",
        "scenario_specific",
        "covid_exogenous_shock",
    }.issubset(set(policy.required_contextual_caveats_zh))


def test_backtest_result_caveat_policy_prohibited_text_patterns_are_defined() -> None:
    policy = load_backtest_result_caveat_policy(POLICY_PATH)
    patterns = {
        pattern
        for values in policy.prohibited_text_patterns.values()
        for pattern in values
    }

    assert {
        "目前建議",
        "建議買進",
        "建議賣出",
        "買進訊號",
        "賣出訊號",
        "target weight",
        "investment advice",
    }.issubset(patterns)


def test_backtest_result_caveat_policy_prohibits_unsafe_result_fields() -> None:
    policy = load_backtest_result_caveat_policy(POLICY_PATH)

    assert {
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
        "public_dashboard_output",
        "current_phase_override",
        "decision_status_override",
    }.issubset(set(policy.prohibited_result_fields))
