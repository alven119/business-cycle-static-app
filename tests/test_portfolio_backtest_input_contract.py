from __future__ import annotations

from pathlib import Path

from business_cycle.portfolio import (
    load_portfolio_backtest_input_contract,
    load_portfolio_backtest_scenario_mapping,
    summarize_portfolio_backtest_input_contract,
    validate_portfolio_backtest_input_contract,
    validate_portfolio_backtest_scenario_mapping,
)

CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_input_contract.yaml")
MAPPING_PATH = Path("specs/portfolio/portfolio_backtest_scenario_mapping.yaml")


def test_portfolio_backtest_input_contract_yaml_can_be_loaded() -> None:
    contract = load_portfolio_backtest_input_contract(CONTRACT_PATH)

    assert contract.version == 1
    assert contract.status == "draft"
    validate_portfolio_backtest_input_contract(contract)


def test_portfolio_backtest_scenario_mapping_yaml_can_be_loaded() -> None:
    contract = load_portfolio_backtest_input_contract(CONTRACT_PATH)
    mapping = load_portfolio_backtest_scenario_mapping(MAPPING_PATH)

    assert mapping.version == 1
    assert mapping.status == "draft"
    validate_portfolio_backtest_scenario_mapping(mapping, contract)


def test_portfolio_backtest_contract_summary_counts_and_next_phase() -> None:
    contract = load_portfolio_backtest_input_contract(CONTRACT_PATH)
    mapping = load_portfolio_backtest_scenario_mapping(MAPPING_PATH)
    summary = summarize_portfolio_backtest_input_contract(contract, mapping)

    assert summary["allowed_policy_template_count"] == 3
    assert summary["mapped_scenario_count"] == summary["allowed_scenario_count"]
    assert summary["live_allocation_output_allowed"] is False
    assert summary["trade_signal_output_allowed"] is False
    assert summary["public_dashboard_output_allowed"] is False
    assert summary["recommended_next_phase"] == "8D"


def test_portfolio_backtest_contract_required_metrics_and_safety_fields() -> None:
    contract = load_portfolio_backtest_input_contract(CONTRACT_PATH)
    metrics = set(contract.risk_metric_contract["required_metrics"])
    prohibited_outputs = set(contract.output_contract["prohibited_outputs"])
    prohibited_inputs = set(contract.data_contract["prohibited_inputs_per_period"])

    assert {"max_drawdown", "turnover", "false_de_risk_cost", "false_re_risk_cost"}.issubset(
        metrics
    )
    assert {
        "live_allocation",
        "buy_signal",
        "sell_signal",
        "target_weight",
        "portfolio_action",
        "public_dashboard_output",
    }.issubset(prohibited_outputs)
    assert {
        "live_allocation",
        "target_weight",
        "current_market_recommendation",
    }.issubset(prohibited_inputs)
    assert any(
        "不構成投資建議" in caveat
        for caveat in contract.output_contract["required_output_caveats_zh"]
    )


def test_portfolio_backtest_scenario_mapping_covers_allowed_scenarios() -> None:
    contract = load_portfolio_backtest_input_contract(CONTRACT_PATH)
    mapping = load_portfolio_backtest_scenario_mapping(MAPPING_PATH)

    assert set(contract.allowed_scenarios).issubset(mapping.scenarios)


def test_portfolio_backtest_scenario_mapping_uses_known_templates_and_evidence_families() -> None:
    contract = load_portfolio_backtest_input_contract(CONTRACT_PATH)
    mapping = load_portfolio_backtest_scenario_mapping(MAPPING_PATH)
    known_templates = set(contract.allowed_policy_templates)
    known_families = {"recession_confirmation", "boom_ending_watch", "recovery_watch"}

    for scenario in mapping.scenarios.values():
        assert set(scenario["primary_research_purpose"]).issubset(known_templates)
        assert set(scenario["required_evidence_families"]).issubset(known_families)
        assert scenario["caveats_zh"]
