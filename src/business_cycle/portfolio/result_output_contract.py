"""Load and validate backtest result output contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class BacktestResultOutputContractError(ValueError):
    """Raised when backtest result output contract validation fails."""


@dataclass(frozen=True)
class BacktestResultOutputContract:
    """Machine-readable backtest result output contract."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    source_engine_contract: dict[str, Any]
    output_contract_scope: dict[str, dict[str, Any]]
    result_object_schema: dict[str, Any]
    result_type_policy: dict[str, Any]
    prohibited_result_fields: list[str]
    prohibited_text_patterns: dict[str, list[str]]
    required_result_caveats_zh: list[str]
    output_location_dependency: dict[str, Any]
    result_safety_dependency: dict[str, Any]
    result_caveat_dependency: dict[str, Any]
    required_acceptance_before_result_generation: list[dict[str, Any]]
    phase_9a1_closure: dict[str, Any]
    recommended_next_phase: dict[str, Any]


def load_backtest_result_output_contract(path: str | Path) -> BacktestResultOutputContract:
    """Load and validate backtest result output contract YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BacktestResultOutputContractError(
            f"backtest_result_output_contract file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BacktestResultOutputContractError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BacktestResultOutputContractError(
            "backtest_result_output_contract YAML must be a mapping"
        )
    raw = payload.get("backtest_result_output_contract")
    if not isinstance(raw, dict):
        raise BacktestResultOutputContractError(
            "backtest_result_output_contract YAML must contain a mapping"
        )
    contract = _contract_from_mapping({str(key): value for key, value in raw.items()})
    validate_backtest_result_output_contract(contract)
    return contract


def validate_backtest_result_output_contract(contract: BacktestResultOutputContract) -> None:
    """Validate parsed backtest result output contract."""

    if not isinstance(contract.version, int):
        raise BacktestResultOutputContractError("version must exist and be an integer")
    if not contract.status:
        raise BacktestResultOutputContractError("status must be non-empty")
    if not contract.source_engine_contract:
        raise BacktestResultOutputContractError("source_engine_contract must exist")
    if not contract.output_contract_scope:
        raise BacktestResultOutputContractError("output_contract_scope must exist")
    if not contract.result_object_schema:
        raise BacktestResultOutputContractError("result_object_schema must exist")
    if not contract.result_type_policy:
        raise BacktestResultOutputContractError("result_type_policy must exist")
    if not contract.prohibited_result_fields:
        raise BacktestResultOutputContractError("prohibited_result_fields must exist")
    if not contract.prohibited_text_patterns:
        raise BacktestResultOutputContractError("prohibited_text_patterns must exist")
    if not contract.required_result_caveats_zh:
        raise BacktestResultOutputContractError("required_result_caveats_zh must exist")
    if not contract.output_location_dependency:
        raise BacktestResultOutputContractError("output_location_dependency must exist")
    if not contract.result_safety_dependency:
        raise BacktestResultOutputContractError("result_safety_dependency must exist")
    if not contract.result_caveat_dependency:
        raise BacktestResultOutputContractError("result_caveat_dependency must exist")
    if str(contract.phase_9a1_closure.get("status") or "") != "result_contract_design_only":
        raise BacktestResultOutputContractError(
            "phase_9a1_closure.status must be result_contract_design_only"
        )
    if str(contract.recommended_next_phase.get("phase_id") or "") != "9A2":
        raise BacktestResultOutputContractError("recommended_next_phase.phase_id must be 9A2")
    _validate_scope(contract.output_contract_scope)
    _validate_result_object_schema(contract.result_object_schema)
    _validate_prohibited_fields(contract.prohibited_result_fields)
    _validate_prohibited_text(contract.prohibited_text_patterns)
    _validate_required_caveats(contract.required_result_caveats_zh)
    _validate_output_location_dependency(contract.output_location_dependency)
    _validate_result_safety_dependency(contract.result_safety_dependency)
    _validate_result_caveat_dependency(contract.result_caveat_dependency)
    _validate_caveats(contract.caveats_zh)


def summarize_backtest_result_output_contract(
    contract: BacktestResultOutputContract,
) -> dict[str, Any]:
    """Return a concise machine-readable result output contract summary."""

    validate_backtest_result_output_contract(contract)
    disallowed = contract.output_contract_scope["disallowed_now"]
    schema = contract.result_object_schema
    next_phase = contract.recommended_next_phase
    return {
        "version": contract.version,
        "status": contract.status,
        "required_result_field_count": len(_str_list(schema["required_fields"], "required_fields")),
        "future_metric_field_count": len(
            _str_list(
                schema["allowed_metric_fields_for_future_results"],
                "allowed_metric_fields_for_future_results",
            )
        ),
        "prohibited_result_field_count": len(contract.prohibited_result_fields),
        "prohibited_auto_write_location_count": len(
            _str_list(
                contract.output_location_dependency["prohibited_auto_write_locations"],
                "prohibited_auto_write_locations",
            )
        ),
        "produce_backtest_results_allowed": not bool(disallowed["produce_backtest_results"]),
        "compute_metric_values_allowed": not bool(disallowed["compute_metric_values"]),
        "write_result_files_allowed": not bool(disallowed["write_result_files"]),
        "write_data_backtests_output_allowed": not bool(
            disallowed["write_data_backtests_output"]
        ),
        "write_public_output_allowed": not bool(disallowed["write_public_output"]),
        "produce_allocation_allowed": not bool(disallowed["produce_allocation"]),
        "produce_trade_signal_allowed": not bool(disallowed["produce_trade_signal"]),
        "metric_values_allowed_now": bool(schema["metric_values_allowed_now"]),
        "auto_write_allowed_now": bool(
            contract.output_location_dependency["auto_write_allowed_now"]
        ),
        "phase_9a1_closure_status": contract.phase_9a1_closure["status"],
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _contract_from_mapping(payload: dict[str, Any]) -> BacktestResultOutputContract:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "source_engine_contract",
        "output_contract_scope",
        "result_object_schema",
        "result_type_policy",
        "prohibited_result_fields",
        "prohibited_text_patterns",
        "required_result_caveats_zh",
        "output_location_dependency",
        "result_safety_dependency",
        "result_caveat_dependency",
        "required_acceptance_before_result_generation",
        "phase_9a1_closure",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise BacktestResultOutputContractError(
            "backtest_result_output_contract missing required field(s): "
            f"{', '.join(missing)}"
        )
    return BacktestResultOutputContract(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        source_engine_contract=_mapping(payload["source_engine_contract"], "source_engine_contract"),
        output_contract_scope=_mapping_of_mappings(
            payload["output_contract_scope"],
            "output_contract_scope",
        ),
        result_object_schema=_mapping(payload["result_object_schema"], "result_object_schema"),
        result_type_policy=_mapping(payload["result_type_policy"], "result_type_policy"),
        prohibited_result_fields=_str_list(
            payload["prohibited_result_fields"],
            "prohibited_result_fields",
        ),
        prohibited_text_patterns=_mapping_of_str_lists(
            payload["prohibited_text_patterns"],
            "prohibited_text_patterns",
        ),
        required_result_caveats_zh=_str_list(
            payload["required_result_caveats_zh"],
            "required_result_caveats_zh",
        ),
        output_location_dependency=_mapping(
            payload["output_location_dependency"],
            "output_location_dependency",
        ),
        result_safety_dependency=_mapping(
            payload["result_safety_dependency"],
            "result_safety_dependency",
        ),
        result_caveat_dependency=_mapping(
            payload["result_caveat_dependency"],
            "result_caveat_dependency",
        ),
        required_acceptance_before_result_generation=_list_of_mappings(
            payload["required_acceptance_before_result_generation"],
            "required_acceptance_before_result_generation",
        ),
        phase_9a1_closure=_mapping(payload["phase_9a1_closure"], "phase_9a1_closure"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_scope(scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(scope.get("disallowed_now"), "output_contract_scope.disallowed_now")
    for field in (
        "produce_backtest_results",
        "compute_metric_values",
        "write_result_files",
        "write_data_backtests_output",
        "write_public_output",
        "produce_allocation",
        "produce_trade_signal",
    ):
        if disallowed.get(field) is not True:
            raise BacktestResultOutputContractError(
                f"output_contract_scope.disallowed_now.{field} must be true"
            )


def _validate_result_object_schema(schema: dict[str, Any]) -> None:
    if schema.get("metric_fields_allowed_now") is not False:
        raise BacktestResultOutputContractError(
            "result_object_schema.metric_fields_allowed_now must be false"
        )
    if schema.get("metric_values_allowed_now") is not False:
        raise BacktestResultOutputContractError(
            "result_object_schema.metric_values_allowed_now must be false"
        )
    metrics = set(
        _str_list(
            schema.get("allowed_metric_fields_for_future_results"),
            "allowed_metric_fields_for_future_results",
        )
    )
    required = {
        "total_return",
        "annualized_return",
        "volatility",
        "max_drawdown",
        "turnover",
        "whipsaw_count",
        "false_de_risk_cost",
        "false_re_risk_cost",
    }
    missing = sorted(required - metrics)
    if missing:
        raise BacktestResultOutputContractError(
            f"allowed_metric_fields_for_future_results missing field(s): {', '.join(missing)}"
        )


def _validate_prohibited_fields(fields: list[str]) -> None:
    required = {
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
        "public_dashboard_output",
        "current_phase_override",
        "decision_status_override",
    }
    missing = sorted(required - set(fields))
    if missing:
        raise BacktestResultOutputContractError(
            f"prohibited_result_fields missing field(s): {', '.join(missing)}"
        )


def _validate_prohibited_text(patterns_by_language: dict[str, list[str]]) -> None:
    patterns = {pattern for values in patterns_by_language.values() for pattern in values}
    required = {
        "目前建議",
        "建議買進",
        "建議賣出",
        "買進訊號",
        "賣出訊號",
        "buy signal",
        "sell signal",
        "investment advice",
    }
    missing = sorted(required - patterns)
    if missing:
        raise BacktestResultOutputContractError(
            f"prohibited_text_patterns missing pattern(s): {', '.join(missing)}"
        )


def _validate_required_caveats(caveats: list[str]) -> None:
    required = {
        "backtest-only，不是目前配置建議。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }
    missing = sorted(required - set(caveats))
    if missing:
        raise BacktestResultOutputContractError(
            f"required_result_caveats_zh missing caveat(s): {', '.join(missing)}"
        )


def _validate_output_location_dependency(dependency: dict[str, Any]) -> None:
    if dependency.get("auto_write_allowed_now") is not False:
        raise BacktestResultOutputContractError(
            "output_location_dependency.auto_write_allowed_now must be false"
        )
    locations = set(
        _str_list(
            dependency.get("prohibited_auto_write_locations"),
            "output_location_dependency.prohibited_auto_write_locations",
        )
    )
    required = {"public", "dashboard", "github_pages", "data/backtests"}
    missing = sorted(required - locations)
    if missing:
        raise BacktestResultOutputContractError(
            "output_location_dependency.prohibited_auto_write_locations missing "
            f"location(s): {', '.join(missing)}"
        )


def _validate_result_safety_dependency(dependency: dict[str, Any]) -> None:
    if dependency.get("required_before_generating_results") is not True:
        raise BacktestResultOutputContractError(
            "result_safety_dependency.required_before_generating_results must be true"
        )


def _validate_result_caveat_dependency(dependency: dict[str, Any]) -> None:
    if dependency.get("required_before_generating_results") is not True:
        raise BacktestResultOutputContractError(
            "result_caveat_dependency.required_before_generating_results must be true"
        )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise BacktestResultOutputContractError("caveats_zh must include 不構成投資建議")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BacktestResultOutputContractError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise BacktestResultOutputContractError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _mapping_of_str_lists(value: Any, field: str) -> dict[str, list[str]]:
    mapping = _mapping(value, field)
    return {key: _str_list(raw, f"{field}.{key}") for key, raw in mapping.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BacktestResultOutputContractError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise BacktestResultOutputContractError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BacktestResultOutputContractError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise BacktestResultOutputContractError(f"{field} must not contain empty items")
    return result
