"""Load and validate real backtest prototype readiness gates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class RealBacktestPrototypeReadinessGateError(ValueError):
    """Raised when real backtest prototype readiness gate validation fails."""


@dataclass(frozen=True)
class RealBacktestPrototypeReadinessGate:
    """Machine-readable real backtest prototype readiness gate."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    current_phase_8_closure: dict[str, Any]
    readiness_scope: dict[str, dict[str, Any]]
    required_contracts_before_real_backtest: dict[str, dict[str, Any]]
    prototype_blockers: list[dict[str, Any]]
    allowed_future_phases: list[dict[str, Any]]
    required_acceptance_before_phase_9A: list[dict[str, Any]]
    readiness_conclusion: dict[str, Any]
    recommended_next_phase: dict[str, Any]


def load_real_backtest_prototype_readiness_gate(
    path: str | Path,
) -> RealBacktestPrototypeReadinessGate:
    """Load and validate real backtest prototype readiness gate YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise RealBacktestPrototypeReadinessGateError(
            f"real_backtest_prototype_readiness_gate file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RealBacktestPrototypeReadinessGateError(
            f"Invalid YAML in {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise RealBacktestPrototypeReadinessGateError(
            "real_backtest_prototype_readiness_gate YAML must be a mapping"
        )
    raw = payload.get("real_backtest_prototype_readiness_gate")
    if not isinstance(raw, dict):
        raise RealBacktestPrototypeReadinessGateError(
            "real_backtest_prototype_readiness_gate YAML must contain a mapping"
        )
    gate = _gate_from_mapping({str(key): value for key, value in raw.items()})
    validate_real_backtest_prototype_readiness_gate(gate)
    return gate


def validate_real_backtest_prototype_readiness_gate(
    gate: RealBacktestPrototypeReadinessGate,
) -> None:
    """Validate parsed real backtest prototype readiness gate."""

    if not isinstance(gate.version, int):
        raise RealBacktestPrototypeReadinessGateError("version must exist and be an integer")
    if not gate.status:
        raise RealBacktestPrototypeReadinessGateError("status must be non-empty")
    if not gate.current_phase_8_closure:
        raise RealBacktestPrototypeReadinessGateError("current_phase_8_closure must exist")
    if not gate.readiness_scope:
        raise RealBacktestPrototypeReadinessGateError("readiness_scope must exist")
    if not gate.required_contracts_before_real_backtest:
        raise RealBacktestPrototypeReadinessGateError(
            "required_contracts_before_real_backtest must exist"
        )
    if not gate.prototype_blockers:
        raise RealBacktestPrototypeReadinessGateError("prototype_blockers must exist")
    if not gate.allowed_future_phases:
        raise RealBacktestPrototypeReadinessGateError("allowed_future_phases must exist")
    if not gate.required_acceptance_before_phase_9A:
        raise RealBacktestPrototypeReadinessGateError(
            "required_acceptance_before_phase_9A must exist"
        )
    if str(gate.readiness_conclusion.get("status") or "") != "ready_for_contract_design_only":
        raise RealBacktestPrototypeReadinessGateError(
            "readiness_conclusion.status must be ready_for_contract_design_only"
        )
    if str(gate.recommended_next_phase.get("phase_id") or "") != "9A":
        raise RealBacktestPrototypeReadinessGateError("recommended_next_phase.phase_id must be 9A")
    _validate_phase_8_closure(gate.current_phase_8_closure)
    _validate_readiness_scope(gate.readiness_scope)
    _validate_required_contracts(gate.required_contracts_before_real_backtest)
    _validate_active_blockers(gate.prototype_blockers)
    _validate_caveats(gate.caveats_zh)


def summarize_real_backtest_prototype_readiness_gate(
    gate: RealBacktestPrototypeReadinessGate,
) -> dict[str, Any]:
    """Return a concise machine-readable readiness gate summary."""

    validate_real_backtest_prototype_readiness_gate(gate)
    closure = gate.current_phase_8_closure
    disallowed = gate.readiness_scope["disallowed_now"]
    next_phase = gate.recommended_next_phase
    return {
        "version": gate.version,
        "status": gate.status,
        "required_contract_count": len(gate.required_contracts_before_real_backtest),
        "active_blocker_count": sum(
            1 for blocker in gate.prototype_blockers if blocker.get("active") is True
        ),
        "allowed_future_phase_count": len(gate.allowed_future_phases),
        "readiness_conclusion_status": gate.readiness_conclusion["status"],
        "research_only_required": bool(closure["research_only_required"]),
        "structural_dry_run_only_required": bool(closure["structural_dry_run_only_required"]),
        "real_backtest_execution_allowed": not bool(disallowed["implement_real_backtest_engine"]),
        "performance_metrics_allowed": not bool(disallowed["compute_performance_metrics"]),
        "backtest_result_output_allowed": not bool(disallowed["produce_backtest_results"]),
        "allocation_output_allowed": not bool(disallowed["produce_allocation"]),
        "trade_signal_output_allowed": not bool(disallowed["produce_trade_signal"]),
        "data_backtests_output_allowed": not bool(disallowed["write_data_backtests_output"]),
        "public_output_allowed": not bool(disallowed["write_public_output"]),
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _gate_from_mapping(payload: dict[str, Any]) -> RealBacktestPrototypeReadinessGate:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "current_phase_8_closure",
        "readiness_scope",
        "required_contracts_before_real_backtest",
        "prototype_blockers",
        "allowed_future_phases",
        "required_acceptance_before_phase_9A",
        "readiness_conclusion",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise RealBacktestPrototypeReadinessGateError(
            "real_backtest_prototype_readiness_gate missing required field(s): "
            f"{', '.join(missing)}"
        )
    return RealBacktestPrototypeReadinessGate(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        current_phase_8_closure=_mapping(
            payload["current_phase_8_closure"],
            "current_phase_8_closure",
        ),
        readiness_scope=_mapping_of_mappings(payload["readiness_scope"], "readiness_scope"),
        required_contracts_before_real_backtest=_mapping_of_mappings(
            payload["required_contracts_before_real_backtest"],
            "required_contracts_before_real_backtest",
        ),
        prototype_blockers=_list_of_mappings(payload["prototype_blockers"], "prototype_blockers"),
        allowed_future_phases=_list_of_mappings(
            payload["allowed_future_phases"],
            "allowed_future_phases",
        ),
        required_acceptance_before_phase_9A=_list_of_mappings(
            payload["required_acceptance_before_phase_9A"],
            "required_acceptance_before_phase_9A",
        ),
        readiness_conclusion=_mapping(payload["readiness_conclusion"], "readiness_conclusion"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_phase_8_closure(closure: dict[str, Any]) -> None:
    expected = {
        "research_only_required": True,
        "structural_dry_run_only_required": True,
        "formal_backtest_executed_required": False,
        "performance_metrics_computed_required": False,
        "allocation_output_generated_required": False,
        "trade_signal_generated_required": False,
        "data_backtests_output_written_required": False,
        "public_output_written_required": False,
    }
    for field, expected_value in expected.items():
        if closure.get(field) is not expected_value:
            raise RealBacktestPrototypeReadinessGateError(
                f"current_phase_8_closure.{field} must be {str(expected_value).lower()}"
            )


def _validate_readiness_scope(scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(scope.get("disallowed_now"), "readiness_scope.disallowed_now")
    for field in (
        "implement_real_backtest_engine",
        "compute_performance_metrics",
        "produce_backtest_results",
        "write_data_backtests_output",
        "write_public_output",
        "produce_allocation",
        "produce_trade_signal",
    ):
        if disallowed.get(field) is not True:
            raise RealBacktestPrototypeReadinessGateError(
                f"readiness_scope.disallowed_now.{field} must be true"
            )


def _validate_required_contracts(contracts: dict[str, dict[str, Any]]) -> None:
    required = {
        "real_backtest_engine_contract",
        "backtest_result_output_contract",
        "metric_formula_registry",
        "backtest_result_safety_validator",
        "output_location_policy",
        "result_caveat_policy",
    }
    missing = sorted(required - set(contracts))
    if missing:
        raise RealBacktestPrototypeReadinessGateError(
            "required_contracts_before_real_backtest missing contract(s): "
            f"{', '.join(missing)}"
        )
    for contract_id in required:
        if contracts[contract_id].get("required") is not True:
            raise RealBacktestPrototypeReadinessGateError(f"{contract_id}.required must be true")


def _validate_active_blockers(blockers: list[dict[str, Any]]) -> None:
    if not any(blocker.get("active") is True for blocker in blockers):
        raise RealBacktestPrototypeReadinessGateError(
            "prototype_blockers must include at least one active blocker"
        )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise RealBacktestPrototypeReadinessGateError("caveats_zh must include 不構成投資建議")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RealBacktestPrototypeReadinessGateError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise RealBacktestPrototypeReadinessGateError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RealBacktestPrototypeReadinessGateError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise RealBacktestPrototypeReadinessGateError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RealBacktestPrototypeReadinessGateError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise RealBacktestPrototypeReadinessGateError(f"{field} must not contain empty items")
    return result
