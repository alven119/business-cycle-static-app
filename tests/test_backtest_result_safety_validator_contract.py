from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_backtest_result_safety_validator_contract,
    summarize_backtest_result_safety_validator_contract,
    validate_backtest_result_safety_validator_contract,
)

CONTRACT_PATH = Path("specs/portfolio/backtest_result_safety_validator_contract.yaml")


def test_backtest_result_safety_validator_contract_yaml_can_be_loaded() -> None:
    contract = load_backtest_result_safety_validator_contract(CONTRACT_PATH)

    assert contract.version == 1
    assert contract.status == "draft"
    validate_backtest_result_safety_validator_contract(contract)


def test_backtest_result_safety_validator_contract_summary_blocks_runtime() -> None:
    contract = load_backtest_result_safety_validator_contract(CONTRACT_PATH)
    summary = summarize_backtest_result_safety_validator_contract(contract)

    assert summary["safety_check_group_count"] >= 8
    assert summary["prohibited_result_field_count"] >= 16
    assert summary["prohibited_text_pattern_count"] > 0
    assert summary["required_global_caveat_count"] >= 4
    assert summary["run_validator_on_real_results_allowed"] is False
    assert summary["produce_backtest_results_allowed"] is False
    assert summary["compute_metric_values_allowed"] is False
    assert summary["write_result_files_allowed"] is False
    assert summary["write_data_backtests_output_allowed"] is False
    assert summary["write_public_output_allowed"] is False
    assert summary["create_output_directories_allowed"] is False
    assert summary["produce_allocation_allowed"] is False
    assert summary["produce_trade_signal_allowed"] is False
    assert summary["public_auto_output_allowed"] is False
    assert summary["data_backtests_write_allowed_now"] is False
    assert summary["validator_runtime_allowed_now"] is False
    assert summary["real_result_validation_allowed_now"] is False
    assert summary["phase_9a5_closure_status"] == "safety_validator_contract_design_only"
    assert summary["recommended_next_phase"] == "9A6"


def test_backtest_result_safety_validator_contract_required_check_groups_exist() -> None:
    contract = load_backtest_result_safety_validator_contract(CONTRACT_PATH)
    group_ids = {
        group["check_group_id"]
        for group in contract.safety_check_groups["required_check_groups"]
    }

    assert {
        "prohibited_field_checks",
        "prohibited_text_checks",
        "required_caveat_checks",
        "caveat_visibility_checks",
        "output_location_checks",
        "metadata_caveat_checks",
        "scenario_specific_caveat_checks",
        "no_live_decision_checks",
    }.issubset(group_ids)


def test_backtest_result_safety_validator_contract_prohibits_unsafe_fields() -> None:
    contract = load_backtest_result_safety_validator_contract(CONTRACT_PATH)

    assert {
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
        "public_dashboard_output",
        "current_phase_override",
        "decision_status_override",
    }.issubset(set(contract.prohibited_result_fields))


def test_backtest_result_safety_validator_contract_prohibits_unsafe_text() -> None:
    contract = load_backtest_result_safety_validator_contract(CONTRACT_PATH)
    patterns = {
        pattern
        for values in contract.prohibited_text_patterns.values()
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


def test_backtest_result_safety_validator_contract_required_caveats_exist() -> None:
    contract = load_backtest_result_safety_validator_contract(CONTRACT_PATH)
    caveats = set(contract.required_caveat_checks["required_global_caveats_zh"])

    assert {
        "backtest-only，不是目前配置建議。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }.issubset(caveats)
