from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_real_backtest_execution_readiness_closure,
    summarize_real_backtest_execution_readiness_closure,
    validate_real_backtest_execution_readiness_closure,
)

CLOSURE_PATH = Path("specs/portfolio/real_backtest_execution_readiness_closure.yaml")


def test_real_backtest_execution_readiness_closure_yaml_can_be_loaded() -> None:
    closure = load_real_backtest_execution_readiness_closure(CLOSURE_PATH)

    assert closure.version == 1
    assert closure.status == "draft"
    validate_real_backtest_execution_readiness_closure(closure)


def test_real_backtest_execution_readiness_closure_summary_blocks_execution() -> None:
    closure = load_real_backtest_execution_readiness_closure(CLOSURE_PATH)
    summary = summarize_real_backtest_execution_readiness_closure(closure)

    assert summary["source_artifact_count"] == 10
    assert summary["validator_command_count"] >= 8
    assert summary["remaining_output_write_blocker_count"] >= 4
    assert summary["phase_9a_contract_stack_complete"] is True
    assert summary["real_backtest_execution_allowed_now"] is False
    assert summary["engine_runtime_allowed_now"] is False
    assert summary["writer_runtime_allowed_now"] is False
    assert summary["real_result_validator_runtime_allowed_now"] is False
    assert summary["metric_computation_allowed_now"] is False
    assert summary["result_generation_allowed_now"] is False
    assert summary["result_file_write_allowed_now"] is False
    assert summary["output_directory_creation_allowed_now"] is False
    assert summary["data_backtests_write_allowed_now"] is False
    assert summary["public_write_allowed_now"] is False
    assert summary["allocation_output_allowed_now"] is False
    assert summary["trade_signal_output_allowed_now"] is False
    assert summary["live_recommendation_allowed_now"] is False
    assert summary["controlled_9b_prototype_entry_allowed"] is True
    assert summary["default_9b_output_write_allowed"] is False
    assert summary["phase_9a8_closure_status"] == "ready_for_controlled_9b_prototype"
    assert summary["recommended_next_phase"] == "9B"


def test_real_backtest_execution_readiness_closure_recommends_controlled_9b_scope() -> None:
    closure = load_real_backtest_execution_readiness_closure(CLOSURE_PATH)
    entry = closure.phase_9b_entry_conditions

    assert entry["default_output_write_allowed"] is False
    assert entry["default_public_output_allowed"] is False
    assert entry["default_allocation_output_allowed"] is False
    assert entry["default_trade_signal_allowed"] is False
    assert "no_dashboard_integration" in entry["required_9b_runtime_constraints"]
    assert "no_live_allocation" in entry["required_9b_runtime_constraints"]
    assert "no_trade_signal" in entry["required_9b_runtime_constraints"]
    assert "controlled synthetic in-memory calculation harness" in entry[
        "recommended_9b_initial_scope_zh"
    ]


def test_real_backtest_execution_readiness_closure_caveats_and_no_output_directory() -> None:
    closure = load_real_backtest_execution_readiness_closure(CLOSURE_PATH)

    assert any("不構成投資建議" in caveat for caveat in closure.caveats_zh)
    assert not Path("data/backtests/research").exists()
