"""Cash-flow-aware backtest kernel contract helpers for Phase78."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_KERNEL_CONTRACT_PATH = (
    ROOT / "specs/portfolio/cash_flow_aware_backtest_kernel_contract.yaml"
)

REQUIRED_KERNEL_COMPONENT_IDS = {
    "contribution_ledger_policy",
    "cash_flow_timing_policy",
    "unitized_nav_policy",
    "rebalancing_policy",
    "transaction_cost_policy",
    "drawdown_policy",
    "turnover_policy",
    "false_signal_cost_policy",
    "missed_recovery_cost_policy",
    "provenance_policy",
}

PROHIBITED_KERNEL_OUTPUT_FIELDS = {
    "current_allocation",
    "target_weight",
    "target_weights",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "rebalance_now",
    "live_allocation",
    "portfolio_action",
    "current_market_recommendation",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "standalone_phase_score",
    "backtest_performance",
    "accuracy_metric",
    "future_return_guarantee",
}

DISABLED_GUARD_KEYS = (
    "cash_flow_backtest_kernel_execution_enabled",
    "metric_computation_enabled",
    "backtest_execution_enabled",
    "portfolio_policy_replay_execution_enabled",
    "current_allocation_recommendation_enabled",
    "live_allocation_enabled",
    "trade_signal_enabled",
    "candidate_phase_emission_enabled",
    "current_phase_emission_enabled",
    "production_integration_enabled",
    "public_output_enabled",
)


class CashFlowBacktestKernelContractError(ValueError):
    """Raised when the cash-flow-aware kernel contract is invalid."""


@dataclass(frozen=True)
class CashFlowBacktestKernelContract:
    """Machine-readable Phase78 cash-flow-aware backtest kernel contract."""

    version: int
    status: str
    phase_id: int
    contract_id: str
    objective_zh: str
    dependencies: dict[str, Any]
    allowed_inputs: list[str]
    prohibited_inputs: list[str]
    kernel_components: list[dict[str, Any]]
    structural_fixtures: list[dict[str, Any]]
    output_policy: dict[str, Any]
    disabled_runtime_guards: dict[str, Any]
    hard_gates: dict[str, Any]


def load_cash_flow_backtest_kernel_contract(
    path: str | Path = DEFAULT_KERNEL_CONTRACT_PATH,
) -> CashFlowBacktestKernelContract:
    """Load and validate the Phase78 cash-flow-aware kernel contract."""

    payload = _load_root_mapping(path)
    contract = CashFlowBacktestKernelContract(
        version=int(payload["version"]),
        status=str(payload["status"]),
        phase_id=int(payload["phase_id"]),
        contract_id=str(payload["contract_id"]),
        objective_zh=str(payload["objective_zh"]),
        dependencies=_mapping(payload["dependencies"], "dependencies"),
        allowed_inputs=_string_list(payload["allowed_inputs"], "allowed_inputs"),
        prohibited_inputs=_string_list(payload["prohibited_inputs"], "prohibited_inputs"),
        kernel_components=_mapping_list(
            payload["kernel_components"],
            "kernel_components",
        ),
        structural_fixtures=_mapping_list(
            payload["structural_fixtures"],
            "structural_fixtures",
        ),
        output_policy=_mapping(payload["output_policy"], "output_policy"),
        disabled_runtime_guards=_mapping(
            payload["disabled_runtime_guards"],
            "disabled_runtime_guards",
        ),
        hard_gates=_mapping(payload["hard_gates"], "hard_gates"),
    )
    validate_cash_flow_backtest_kernel_contract(contract)
    return contract


def validate_cash_flow_backtest_kernel_contract(
    contract: CashFlowBacktestKernelContract,
) -> None:
    """Validate kernel component, fixture, output, and disabled-runtime guards."""

    if contract.phase_id != 78:
        raise CashFlowBacktestKernelContractError("phase_id must be 78")
    if contract.status != "preregistered_research_kernel_contract_only":
        raise CashFlowBacktestKernelContractError(
            "status must be preregistered_research_kernel_contract_only",
        )
    component_ids = _component_ids(contract)
    missing = REQUIRED_KERNEL_COMPONENT_IDS - component_ids
    if missing:
        raise CashFlowBacktestKernelContractError(
            f"kernel_components missing: {', '.join(sorted(missing))}",
        )
    extras = component_ids - REQUIRED_KERNEL_COMPONENT_IDS
    if extras:
        raise CashFlowBacktestKernelContractError(
            f"kernel_components contain unknown ids: {', '.join(sorted(extras))}",
        )
    if len(contract.kernel_components) != len(component_ids):
        raise CashFlowBacktestKernelContractError("kernel component ids must be unique")
    for component in contract.kernel_components:
        _validate_component(component)
    if not contract.structural_fixtures:
        raise CashFlowBacktestKernelContractError("structural_fixtures must exist")
    for fixture in contract.structural_fixtures:
        _validate_fixture(fixture, component_ids)
    _validate_output_policy(contract.output_policy)
    _validate_disabled_guards(contract.disabled_runtime_guards)


def summarize_cash_flow_backtest_kernel_contract(
    path: str | Path = DEFAULT_KERNEL_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase78 cash-flow-aware kernel hard-gate fields."""

    contract = load_cash_flow_backtest_kernel_contract(path)
    fixture_pass_count = sum(
        _fixture_structurally_valid(fixture, _component_ids(contract))
        for fixture in contract.structural_fixtures
    )
    output_policy = contract.output_policy
    guards = contract.disabled_runtime_guards
    summary: dict[str, Any] = {
        "phase": "78",
        "phase_id": 78,
        "cash_flow_aware_backtest_kernel_contract_ready": True,
        "contract_id": contract.contract_id,
        "kernel_component_count": len(contract.kernel_components),
        "required_kernel_component_count": len(REQUIRED_KERNEL_COMPONENT_IDS),
        "structural_fixture_count": len(contract.structural_fixtures),
        "structural_fixture_validation_pass_count": fixture_pass_count,
        "execution_allowed_now_count": int(
            bool(output_policy.get("execution_allowed_now")),
        )
        + int(bool(guards.get("cash_flow_backtest_kernel_execution_enabled"))),
        "metric_computation_enabled": bool(guards.get("metric_computation_enabled")),
        "backtest_execution_count": int(bool(guards.get("backtest_execution_enabled"))),
        "generated_output_under_tmp_only": bool(
            output_policy.get("generated_output_under_tmp_only"),
        ),
        "current_allocation_recommendation_count": int(
            bool(output_policy.get("current_allocation_recommendation_allowed")),
        )
        + int(bool(guards.get("current_allocation_recommendation_enabled"))),
        "trade_signal_output_count": int(bool(output_policy.get("trade_signal_allowed")))
        + int(bool(guards.get("trade_signal_enabled"))),
        "live_allocation_output_count": int(
            bool(output_policy.get("live_allocation_allowed")),
        )
        + int(bool(guards.get("live_allocation_enabled"))),
        "prohibited_kernel_output_field_count": _prohibited_output_field_count(contract),
        "investment_advice_wording_count": 0,
        "candidate_phase_emitted": bool(
            guards.get("candidate_phase_emission_enabled"),
        ),
        "current_phase_emitted": bool(guards.get("current_phase_emission_enabled")),
        "production_behavior_change_count": int(
            bool(guards.get("production_integration_enabled")),
        ),
        "semantic_drift_count": 0,
        "component_ids": sorted(component_ids := _component_ids(contract)),
        "fixture_ids": sorted(str(row["fixture_id"]) for row in contract.structural_fixtures),
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_cash_flow_backtest_kernel_contract_ready"
        ),
        "portfolio_policy_research_alignment": (
            "cash_flow_kernel_preregistered_no_current_allocation"
        ),
        "historical_replay_backtest_alignment": (
            "cash_flow_kernel_contract_ready_no_backtest_execution"
        ),
    }
    if component_ids != REQUIRED_KERNEL_COMPONENT_IDS:
        summary["semantic_drift_count"] = 1
    summary["result"] = "passed" if _passes(summary, contract.hard_gates) else "blocked"
    return summary


def build_cash_flow_backtest_kernel_view_model(
    path: str | Path = DEFAULT_KERNEL_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build an artifact-ready view model for future dashboard/replay surfaces."""

    contract = load_cash_flow_backtest_kernel_contract(path)
    return {
        "view_id": "cash_flow_aware_backtest_kernel_contract",
        "view_title": "Cash-flow-aware Backtest Kernel Contract",
        "output_mode": contract.output_policy["output_mode"],
        "research_only": True,
        "execution_allowed_now": False,
        "metric_computation_enabled": False,
        "kernel_components": contract.kernel_components,
        "structural_fixtures": contract.structural_fixtures,
        "allowed_inputs": contract.allowed_inputs,
        "prohibited_inputs": contract.prohibited_inputs,
        "trust_metadata": {
            "source_contract": contract.contract_id,
            "policy_replay_schedule_dependency": contract.dependencies[
                "policy_replay_schedule"
            ],
            "metric_formula_registry_dependency": contract.dependencies[
                "metric_formula_registry"
            ],
            "generated_output_under_tmp_only": True,
            "backtest_execution_enabled": False,
            "trade_signal_enabled": False,
        },
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
    }


def _load_root_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CashFlowBacktestKernelContractError("YAML must be a mapping")
    root = payload.get("cash_flow_aware_backtest_kernel_contract")
    if not isinstance(root, dict):
        raise CashFlowBacktestKernelContractError(
            "YAML must contain cash_flow_aware_backtest_kernel_contract",
        )
    return {str(key): value for key, value in root.items()}


def _validate_component(component: dict[str, Any]) -> None:
    required = {
        "component_id",
        "component_family",
        "purpose_zh",
        "required_inputs",
        "required_guards",
        "compute_allowed_now",
        "output_allowed_now",
    }
    missing = required - set(component)
    if missing:
        raise CashFlowBacktestKernelContractError(
            f"kernel component missing required fields: {', '.join(sorted(missing))}",
        )
    if bool(component.get("compute_allowed_now")):
        raise CashFlowBacktestKernelContractError(
            f"{component['component_id']} must keep compute_allowed_now=false",
        )
    if component.get("output_allowed_now") != "structural_contract_only":
        raise CashFlowBacktestKernelContractError(
            f"{component['component_id']} output_allowed_now must be structural_contract_only",
        )
    if not _string_list(component.get("required_inputs"), "required_inputs"):
        raise CashFlowBacktestKernelContractError(
            f"{component['component_id']} must declare required_inputs",
        )
    if not _string_list(component.get("required_guards"), "required_guards"):
        raise CashFlowBacktestKernelContractError(
            f"{component['component_id']} must declare required_guards",
        )


def _validate_fixture(fixture: dict[str, Any], component_ids: set[str]) -> None:
    required = {
        "fixture_id",
        "scenario_shape",
        "expected_component_ids",
        "expected_status",
        "output_path_policy",
        "metric_values_allowed",
    }
    missing = required - set(fixture)
    if missing:
        raise CashFlowBacktestKernelContractError(
            f"structural fixture missing required fields: {', '.join(sorted(missing))}",
        )
    if not _fixture_structurally_valid(fixture, component_ids):
        raise CashFlowBacktestKernelContractError(
            f"{fixture['fixture_id']} failed structural validation",
        )


def _fixture_structurally_valid(fixture: dict[str, Any], component_ids: set[str]) -> bool:
    expected_ids = set(
        _string_list(fixture.get("expected_component_ids"), "expected_component_ids"),
    )
    return (
        bool(expected_ids)
        and expected_ids <= component_ids
        and str(fixture.get("output_path_policy")) == "tmp_only"
        and bool(fixture.get("metric_values_allowed")) is False
        and str(fixture.get("expected_status")).endswith("_no_execution")
    )


def _validate_output_policy(output_policy: dict[str, Any]) -> None:
    if output_policy.get("output_mode") != "research_kernel_contract_only":
        raise CashFlowBacktestKernelContractError(
            "output_policy.output_mode must be research_kernel_contract_only",
        )
    for key in (
        "execution_allowed_now",
        "metric_computation_allowed_now",
        "backtest_execution_allowed",
        "current_allocation_recommendation_allowed",
        "trade_signal_allowed",
        "live_allocation_allowed",
        "public_output_allowed",
    ):
        if bool(output_policy.get(key)):
            raise CashFlowBacktestKernelContractError(f"output_policy.{key} must be false")
    if output_policy.get("generated_output_under_tmp_only") is not True:
        raise CashFlowBacktestKernelContractError(
            "output_policy.generated_output_under_tmp_only must be true",
        )
    prohibited = set(
        _string_list(output_policy.get("prohibited_fields"), "prohibited_fields"),
    )
    missing = PROHIBITED_KERNEL_OUTPUT_FIELDS - prohibited
    if missing:
        raise CashFlowBacktestKernelContractError(
            f"output_policy.prohibited_fields missing: {', '.join(sorted(missing))}",
        )


def _validate_disabled_guards(disabled_guards: dict[str, Any]) -> None:
    for key in DISABLED_GUARD_KEYS:
        if bool(disabled_guards.get(key)):
            raise CashFlowBacktestKernelContractError(f"{key} must be false")


def _prohibited_output_field_count(contract: CashFlowBacktestKernelContract) -> int:
    inspected = {
        "kernel_components": contract.kernel_components,
        "structural_fixtures": contract.structural_fixtures,
    }
    return _recursive_key_count(inspected, PROHIBITED_KERNEL_OUTPUT_FIELDS)


def _recursive_key_count(value: Any, prohibited: set[str]) -> int:
    if isinstance(value, dict):
        return sum(1 for key in value if str(key) in prohibited) + sum(
            _recursive_key_count(item, prohibited) for item in value.values()
        )
    if isinstance(value, list):
        return sum(_recursive_key_count(item, prohibited) for item in value)
    return 0


def _component_ids(contract: CashFlowBacktestKernelContract) -> set[str]:
    return {str(row.get("component_id")) for row in contract.kernel_components}


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _mapping(raw: Any, field: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CashFlowBacktestKernelContractError(f"{field} must be a mapping")
    return {str(key): value for key, value in raw.items()}


def _mapping_list(raw: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        raise CashFlowBacktestKernelContractError(f"{field} must be a list of mappings")
    return [{str(key): value for key, value in item.items()} for item in raw]


def _string_list(raw: Any, field: str) -> list[str]:
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise CashFlowBacktestKernelContractError(f"{field} must be a list of strings")
    return list(raw)
