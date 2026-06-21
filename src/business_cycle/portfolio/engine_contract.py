"""Load and validate real backtest engine contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class RealBacktestEngineContractError(ValueError):
    """Raised when real backtest engine contract validation fails."""


@dataclass(frozen=True)
class RealBacktestEngineContract:
    """Machine-readable real backtest engine contract."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    source_readiness_gate: dict[str, Any]
    engine_scope: dict[str, dict[str, Any]]
    required_input_contracts: dict[str, dict[str, Any]]
    required_future_dependency_contracts: dict[str, dict[str, Any]]
    engine_stage_contract: dict[str, Any]
    prohibited_engine_outputs: list[str]
    prohibited_auto_write_locations: list[str]
    required_safety_guards_before_execution: list[dict[str, Any]]
    phase_9a_closure: dict[str, Any]
    recommended_next_phase: dict[str, Any]


def load_real_backtest_engine_contract(path: str | Path) -> RealBacktestEngineContract:
    """Load and validate real backtest engine contract YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise RealBacktestEngineContractError(
            f"real_backtest_engine_contract file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RealBacktestEngineContractError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RealBacktestEngineContractError(
            "real_backtest_engine_contract YAML must be a mapping"
        )
    raw = payload.get("real_backtest_engine_contract")
    if not isinstance(raw, dict):
        raise RealBacktestEngineContractError(
            "real_backtest_engine_contract YAML must contain a mapping"
        )
    contract = _contract_from_mapping({str(key): value for key, value in raw.items()})
    validate_real_backtest_engine_contract(contract)
    return contract


def validate_real_backtest_engine_contract(contract: RealBacktestEngineContract) -> None:
    """Validate parsed real backtest engine contract."""

    if not isinstance(contract.version, int):
        raise RealBacktestEngineContractError("version must exist and be an integer")
    if not contract.status:
        raise RealBacktestEngineContractError("status must be non-empty")
    if not contract.source_readiness_gate:
        raise RealBacktestEngineContractError("source_readiness_gate must exist")
    if not contract.engine_scope:
        raise RealBacktestEngineContractError("engine_scope must exist")
    if not contract.required_input_contracts:
        raise RealBacktestEngineContractError("required_input_contracts must exist")
    if not contract.required_future_dependency_contracts:
        raise RealBacktestEngineContractError(
            "required_future_dependency_contracts must exist"
        )
    if not contract.engine_stage_contract:
        raise RealBacktestEngineContractError("engine_stage_contract must exist")
    if not contract.prohibited_engine_outputs:
        raise RealBacktestEngineContractError("prohibited_engine_outputs must exist")
    if not contract.prohibited_auto_write_locations:
        raise RealBacktestEngineContractError(
            "prohibited_auto_write_locations must exist"
        )
    if not contract.required_safety_guards_before_execution:
        raise RealBacktestEngineContractError(
            "required_safety_guards_before_execution must exist"
        )
    if str(contract.phase_9a_closure.get("status") or "") != "contract_design_only":
        raise RealBacktestEngineContractError(
            "phase_9a_closure.status must be contract_design_only"
        )
    if str(contract.recommended_next_phase.get("phase_id") or "") != "9A1":
        raise RealBacktestEngineContractError("recommended_next_phase.phase_id must be 9A1")
    _validate_engine_scope(contract.engine_scope)
    _validate_future_dependency_contracts(contract.required_future_dependency_contracts)
    _validate_engine_stages(contract.engine_stage_contract)
    _validate_prohibited_outputs(contract.prohibited_engine_outputs)
    _validate_prohibited_write_locations(contract.prohibited_auto_write_locations)
    _validate_caveats(contract.caveats_zh)


def summarize_real_backtest_engine_contract(
    contract: RealBacktestEngineContract,
) -> dict[str, Any]:
    """Return a concise machine-readable engine contract summary."""

    validate_real_backtest_engine_contract(contract)
    disallowed = contract.engine_scope["disallowed_now"]
    next_phase = contract.recommended_next_phase
    return {
        "version": contract.version,
        "status": contract.status,
        "input_contract_count": len(contract.required_input_contracts),
        "future_dependency_contract_count": len(contract.required_future_dependency_contracts),
        "engine_stage_count": len(_stage_mapping(contract)),
        "prohibited_output_count": len(contract.prohibited_engine_outputs),
        "prohibited_auto_write_location_count": len(contract.prohibited_auto_write_locations),
        "implement_engine_runtime_allowed": not bool(disallowed["implement_engine_runtime"]),
        "execute_backtest_allowed": not bool(disallowed["execute_backtest"]),
        "compute_performance_metrics_allowed": not bool(
            disallowed["compute_performance_metrics"]
        ),
        "produce_backtest_results_allowed": not bool(disallowed["produce_backtest_results"]),
        "write_data_backtests_output_allowed": not bool(
            disallowed["write_data_backtests_output"]
        ),
        "write_public_output_allowed": not bool(disallowed["write_public_output"]),
        "produce_allocation_allowed": not bool(disallowed["produce_allocation"]),
        "produce_trade_signal_allowed": not bool(disallowed["produce_trade_signal"]),
        "phase_9a_closure_status": contract.phase_9a_closure["status"],
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _contract_from_mapping(payload: dict[str, Any]) -> RealBacktestEngineContract:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "source_readiness_gate",
        "engine_scope",
        "required_input_contracts",
        "required_future_dependency_contracts",
        "engine_stage_contract",
        "prohibited_engine_outputs",
        "prohibited_auto_write_locations",
        "required_safety_guards_before_execution",
        "phase_9a_closure",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise RealBacktestEngineContractError(
            "real_backtest_engine_contract missing required field(s): "
            f"{', '.join(missing)}"
        )
    return RealBacktestEngineContract(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        source_readiness_gate=_mapping(payload["source_readiness_gate"], "source_readiness_gate"),
        engine_scope=_mapping_of_mappings(payload["engine_scope"], "engine_scope"),
        required_input_contracts=_mapping_of_mappings(
            payload["required_input_contracts"],
            "required_input_contracts",
        ),
        required_future_dependency_contracts=_mapping_of_mappings(
            payload["required_future_dependency_contracts"],
            "required_future_dependency_contracts",
        ),
        engine_stage_contract=_mapping(
            payload["engine_stage_contract"],
            "engine_stage_contract",
        ),
        prohibited_engine_outputs=_str_list(
            payload["prohibited_engine_outputs"],
            "prohibited_engine_outputs",
        ),
        prohibited_auto_write_locations=_str_list(
            payload["prohibited_auto_write_locations"],
            "prohibited_auto_write_locations",
        ),
        required_safety_guards_before_execution=_list_of_mappings(
            payload["required_safety_guards_before_execution"],
            "required_safety_guards_before_execution",
        ),
        phase_9a_closure=_mapping(payload["phase_9a_closure"], "phase_9a_closure"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_engine_scope(scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(scope.get("disallowed_now"), "engine_scope.disallowed_now")
    for field in (
        "implement_engine_runtime",
        "execute_backtest",
        "compute_performance_metrics",
        "produce_backtest_results",
        "write_data_backtests_output",
        "write_public_output",
        "produce_allocation",
        "produce_trade_signal",
    ):
        if disallowed.get(field) is not True:
            raise RealBacktestEngineContractError(
                f"engine_scope.disallowed_now.{field} must be true"
            )


def _validate_future_dependency_contracts(
    dependencies: dict[str, dict[str, Any]],
) -> None:
    required = {
        "metric_formula_registry",
        "backtest_result_output_contract",
        "backtest_result_safety_validator",
        "output_location_policy",
        "result_caveat_policy",
    }
    missing = sorted(required - set(dependencies))
    if missing:
        raise RealBacktestEngineContractError(
            "required_future_dependency_contracts missing contract(s): "
            f"{', '.join(missing)}"
        )
    for dependency_id in required:
        dependency = dependencies[dependency_id]
        if dependency.get("required") is not True:
            raise RealBacktestEngineContractError(f"{dependency_id}.required must be true")
        if dependency.get("required_before_execution") is not True:
            raise RealBacktestEngineContractError(
                f"{dependency_id}.required_before_execution must be true"
            )


def _validate_engine_stages(stage_contract: dict[str, Any]) -> None:
    stages = _stage_mapping_from_contract(stage_contract)
    expected_stages = {
        "load_contracts",
        "validate_inputs",
        "build_time_series_panel",
        "apply_policy_template",
        "compute_metrics",
        "build_result_output",
        "validate_result_safety",
        "write_research_output",
    }
    missing = sorted(expected_stages - set(stages))
    if missing:
        raise RealBacktestEngineContractError(
            f"engine_stage_contract.stages missing stage(s): {', '.join(missing)}"
        )
    expected_statuses = {
        "compute_metrics": "blocked_until_metric_registry",
        "build_result_output": "blocked_until_result_output_contract",
        "write_research_output": "blocked_until_output_location_policy",
    }
    for stage_id, expected in expected_statuses.items():
        if stages[stage_id].get("allowed_now") != expected:
            raise RealBacktestEngineContractError(
                f"{stage_id}.allowed_now must be {expected}"
            )


def _validate_prohibited_outputs(outputs: list[str]) -> None:
    required = {
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
        "public_dashboard_output",
    }
    missing = sorted(required - set(outputs))
    if missing:
        raise RealBacktestEngineContractError(
            f"prohibited_engine_outputs missing field(s): {', '.join(missing)}"
        )


def _validate_prohibited_write_locations(locations: list[str]) -> None:
    required = {"public", "dashboard", "github_pages", "data/backtests"}
    missing = sorted(required - set(locations))
    if missing:
        raise RealBacktestEngineContractError(
            f"prohibited_auto_write_locations missing location(s): {', '.join(missing)}"
        )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise RealBacktestEngineContractError("caveats_zh must include 不構成投資建議")


def _stage_mapping(contract: RealBacktestEngineContract) -> dict[str, dict[str, Any]]:
    return _stage_mapping_from_contract(contract.engine_stage_contract)


def _stage_mapping_from_contract(stage_contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    stages = stage_contract.get("stages")
    if not isinstance(stages, list) or not stages:
        raise RealBacktestEngineContractError("engine_stage_contract.stages must be a non-empty list")
    result: dict[str, dict[str, Any]] = {}
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            raise RealBacktestEngineContractError(
                f"engine_stage_contract.stages[{index}] must be a mapping"
            )
        stage_id = str(stage.get("stage_id") or "")
        if not stage_id:
            raise RealBacktestEngineContractError(
                f"engine_stage_contract.stages[{index}].stage_id must exist"
            )
        result[stage_id] = {str(key): value for key, value in stage.items()}
    return result


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RealBacktestEngineContractError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise RealBacktestEngineContractError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RealBacktestEngineContractError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise RealBacktestEngineContractError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RealBacktestEngineContractError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise RealBacktestEngineContractError(f"{field} must not contain empty items")
    return result
