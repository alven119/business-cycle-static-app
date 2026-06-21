"""Structural dry-run runner for portfolio backtest inputs."""

from __future__ import annotations

from typing import Any

from business_cycle.portfolio.backtest_contract import (
    PortfolioBacktestInputContract,
    PortfolioBacktestInputFixtures,
    PortfolioBacktestScenarioMapping,
    validate_portfolio_backtest_input,
    validate_portfolio_backtest_input_contract,
    validate_portfolio_backtest_scenario_mapping,
)
from business_cycle.portfolio.dry_run_contract import (
    PortfolioBacktestDryRunContract,
    PortfolioBacktestDryRunContractError,
    validate_portfolio_backtest_dry_run_contract,
    validate_portfolio_backtest_dry_run_output,
)


def run_portfolio_backtest_structural_dry_run(
    contract: PortfolioBacktestDryRunContract,
    input_contract: PortfolioBacktestInputContract,
    mapping: PortfolioBacktestScenarioMapping,
    fixtures: PortfolioBacktestInputFixtures,
) -> dict[str, Any]:
    """Validate valid input fixtures and return an in-memory structural dry-run report."""

    validate_portfolio_backtest_dry_run_contract(contract)
    validate_portfolio_backtest_input_contract(input_contract)
    validate_portfolio_backtest_scenario_mapping(mapping, input_contract)

    outputs = []
    for fixture in fixtures.valid_inputs:
        backtest_input = _fixture_input(fixture)
        validate_portfolio_backtest_input(backtest_input, input_contract, mapping)
        output = build_dry_run_output_for_input(backtest_input, contract, input_contract, mapping)
        validate_portfolio_backtest_dry_run_output(output, contract)
        outputs.append(output)

    summary = summarize_dry_run_outputs(outputs)
    validate_dry_run_runner_summary(summary)
    return {"outputs": outputs, "summary": summary}


def build_dry_run_output_for_input(
    backtest_input: dict[str, Any],
    dry_run_contract: PortfolioBacktestDryRunContract,
    input_contract: PortfolioBacktestInputContract,
    mapping: PortfolioBacktestScenarioMapping,
) -> dict[str, Any]:
    """Build one structural dry-run output for a validated backtest input."""

    validate_portfolio_backtest_input(backtest_input, input_contract, mapping)
    next_phase = str(dry_run_contract.recommended_next_phase["phase_id"])
    output = {
        "dry_run_id": f"dryrun_{backtest_input['backtest_input_id']}",
        "backtest_input_id": backtest_input["backtest_input_id"],
        "scenario_id": backtest_input["scenario_id"],
        "policy_template_id": backtest_input["policy_template_id"],
        "parameter_set_id": backtest_input["parameter_set_id"],
        "validation_status": "passed",
        "structural_summary": {
            "input_contract_validated": True,
            "scenario_mapping_validated": True,
            "backtest_input_fixture_validated": True,
            "performance_metrics_computed": False,
            "allocation_generated": False,
            "trade_signal_generated": False,
            "output_written": False,
            "data_backtests_output_written": False,
            "public_output_written": False,
        },
        "required_metric_count": len(backtest_input["required_metrics"]),
        "required_input_count": len(backtest_input["required_inputs_per_period"]),
        "caveats_zh": [
            "dry-run，不是正式回測。",
            "不產生 portfolio allocation。",
            "不構成投資建議。",
        ],
        "next_required_phase": next_phase,
    }
    allowed = set(dry_run_contract.dry_run_output_schema["allowed_fields"])
    return {key: value for key, value in output.items() if key in allowed}


def summarize_dry_run_outputs(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize structural dry-run outputs without writing files or computing performance."""

    invalid_count = sum(1 for output in outputs if output.get("validation_status") != "passed")
    summaries = [output.get("structural_summary", {}) for output in outputs]
    return {
        "dry_run_count": len(outputs),
        "valid_dry_run_count": len(outputs) - invalid_count,
        "invalid_dry_run_count": invalid_count,
        "scenario_count": len({str(output.get("scenario_id")) for output in outputs}),
        "policy_template_count": len({str(output.get("policy_template_id")) for output in outputs}),
        "output_written": any(bool(summary.get("output_written")) for summary in summaries),
        "data_backtests_output_written": any(
            bool(summary.get("data_backtests_output_written")) for summary in summaries
        ),
        "public_output_written": any(
            bool(summary.get("public_output_written")) for summary in summaries
        ),
        "allocation_output_generated": any(
            bool(summary.get("allocation_generated")) for summary in summaries
        ),
        "trade_signal_generated": any(
            bool(summary.get("trade_signal_generated")) for summary in summaries
        ),
        "performance_metrics_computed": any(
            bool(summary.get("performance_metrics_computed")) for summary in summaries
        ),
        "result": "passed" if invalid_count == 0 else "failed",
    }


def validate_dry_run_runner_summary(summary: dict[str, Any]) -> None:
    """Validate aggregate structural dry-run summary safety flags."""

    if int(summary.get("dry_run_count", -1)) < 0:
        raise PortfolioBacktestDryRunContractError("dry_run_count must be non-negative")
    if int(summary.get("invalid_dry_run_count", -1)) != 0:
        raise PortfolioBacktestDryRunContractError("invalid_dry_run_count must be 0")
    for field in (
        "output_written",
        "data_backtests_output_written",
        "public_output_written",
        "allocation_output_generated",
        "trade_signal_generated",
        "performance_metrics_computed",
    ):
        if summary.get(field) is not False:
            raise PortfolioBacktestDryRunContractError(f"{field} must be false")
    if summary.get("result") != "passed":
        raise PortfolioBacktestDryRunContractError("result must be passed")


def _fixture_input(fixture: dict[str, Any]) -> dict[str, Any]:
    backtest_input = fixture.get("input")
    if not isinstance(backtest_input, dict):
        raise PortfolioBacktestDryRunContractError("valid fixture input must be a mapping")
    return {str(key): value for key, value in backtest_input.items()}
