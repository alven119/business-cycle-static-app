from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_real_backtest_prototype_readiness_gate,
    summarize_real_backtest_prototype_readiness_gate,
    validate_real_backtest_prototype_readiness_gate,
)

GATE_PATH = Path("specs/portfolio/real_backtest_prototype_readiness_gate.yaml")


def test_real_backtest_prototype_readiness_gate_yaml_can_be_loaded() -> None:
    gate = load_real_backtest_prototype_readiness_gate(GATE_PATH)

    assert gate.version == 1
    assert gate.status == "draft"
    validate_real_backtest_prototype_readiness_gate(gate)


def test_real_backtest_prototype_readiness_gate_summary_blocks_backtest() -> None:
    gate = load_real_backtest_prototype_readiness_gate(GATE_PATH)
    summary = summarize_real_backtest_prototype_readiness_gate(gate)

    assert summary["required_contract_count"] >= 6
    assert summary["active_blocker_count"] > 0
    assert summary["readiness_conclusion_status"] == "ready_for_contract_design_only"
    assert summary["research_only_required"] is True
    assert summary["structural_dry_run_only_required"] is True
    assert summary["real_backtest_execution_allowed"] is False
    assert summary["performance_metrics_allowed"] is False
    assert summary["backtest_result_output_allowed"] is False
    assert summary["allocation_output_allowed"] is False
    assert summary["trade_signal_output_allowed"] is False
    assert summary["data_backtests_output_allowed"] is False
    assert summary["public_output_allowed"] is False
    assert summary["recommended_next_phase"] == "9A"


def test_real_backtest_prototype_readiness_gate_required_contracts_are_defined() -> None:
    gate = load_real_backtest_prototype_readiness_gate(GATE_PATH)

    assert {
        "real_backtest_engine_contract",
        "backtest_result_output_contract",
        "metric_formula_registry",
        "backtest_result_safety_validator",
        "output_location_policy",
        "result_caveat_policy",
    }.issubset(gate.required_contracts_before_real_backtest)


def test_real_backtest_prototype_readiness_gate_caveats_include_no_investment_advice() -> None:
    gate = load_real_backtest_prototype_readiness_gate(GATE_PATH)

    assert any("不構成投資建議" in caveat for caveat in gate.caveats_zh)
