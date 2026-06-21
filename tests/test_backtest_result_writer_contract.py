from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_backtest_result_writer_contract,
    summarize_backtest_result_writer_contract,
    validate_backtest_result_writer_contract,
)

CONTRACT_PATH = Path("specs/portfolio/backtest_result_writer_contract.yaml")


def test_backtest_result_writer_contract_yaml_can_be_loaded() -> None:
    contract = load_backtest_result_writer_contract(CONTRACT_PATH)

    assert contract.version == 1
    assert contract.status == "draft"
    validate_backtest_result_writer_contract(contract)


def test_backtest_result_writer_contract_summary_blocks_writes() -> None:
    contract = load_backtest_result_writer_contract(CONTRACT_PATH)
    summary = summarize_backtest_result_writer_contract(contract)

    assert summary["prohibited_write_location_count"] >= 10
    assert summary["pre_write_validation_count"] >= 10
    assert summary["writer_status_field_count"] >= 10
    assert summary["explicit_user_command_required"] is True
    assert summary["automatic_write_allowed"] is False
    assert summary["implement_writer_runtime_allowed"] is False
    assert summary["write_result_files_allowed"] is False
    assert summary["create_output_directories_allowed"] is False
    assert summary["write_data_backtests_output_allowed"] is False
    assert summary["write_public_output_allowed"] is False
    assert summary["write_docs_output_allowed"] is False
    assert summary["write_dashboard_output_allowed"] is False
    assert summary["write_github_pages_output_allowed"] is False
    assert summary["execute_backtest_allowed"] is False
    assert summary["compute_metric_values_allowed"] is False
    assert summary["produce_allocation_allowed"] is False
    assert summary["produce_trade_signal_allowed"] is False
    assert summary["writer_runtime_allowed_now"] is False
    assert summary["result_file_write_allowed_now"] is False
    assert summary["output_directory_creation_allowed_now"] is False
    assert summary["data_backtests_write_allowed_now"] is False
    assert summary["public_write_allowed_now"] is False
    assert summary["phase_9a7_closure_status"] == "writer_contract_design_only"
    assert summary["recommended_next_phase"] == "9A8"


def test_backtest_result_writer_contract_future_path_requires_explicit_command() -> None:
    contract = load_backtest_result_writer_contract(CONTRACT_PATH)
    research_path = contract.allowed_future_output_paths["controlled_research_path"]

    assert research_path["path"] == "data/backtests/research"
    assert research_path["allowed_only_after_future_writer_runtime_phase"] is True
    assert research_path["requires_explicit_user_command"] is True
    assert research_path["requires_safety_validator_pass"] is True
    assert research_path["auto_publication_allowed"] is False
    assert research_path["git_tracking_allowed"] is False
    assert not Path("data/backtests/research").exists()


def test_backtest_result_writer_contract_prohibits_write_locations() -> None:
    contract = load_backtest_result_writer_contract(CONTRACT_PATH)

    assert {
        "public",
        "docs",
        "site",
        "dashboard",
        "github_pages",
        "data/backtests",
        "data/raw",
        "specs",
        "src",
        "tests",
    }.issubset(set(contract.prohibited_write_locations))


def test_backtest_result_writer_contract_requires_pre_write_validations() -> None:
    contract = load_backtest_result_writer_contract(CONTRACT_PATH)
    validation_ids = {
        validation["validation_id"]
        for validation in contract.required_pre_write_validations
    }

    assert {
        "result_safety_validator_runtime_available",
        "result_safety_validation_passed",
        "explicit_user_command_present",
        "no_public_auto_output",
        "no_live_allocation_or_trade_signal",
    }.issubset(validation_ids)


def test_backtest_result_writer_contract_prohibits_unsafe_result_fields() -> None:
    contract = load_backtest_result_writer_contract(CONTRACT_PATH)

    assert {
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
        "public_dashboard_output",
        "current_phase_override",
        "decision_status_override",
    }.issubset(set(contract.prohibited_result_fields_for_writer))


def test_backtest_result_writer_contract_required_caveats_exist() -> None:
    contract = load_backtest_result_writer_contract(CONTRACT_PATH)

    assert {
        "backtest-only，不是目前配置建議。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }.issubset(set(contract.required_writer_caveats_zh))
    assert any("不構成投資建議" in caveat for caveat in contract.caveats_zh)
