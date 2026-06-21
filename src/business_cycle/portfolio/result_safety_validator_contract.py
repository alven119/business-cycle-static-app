"""Load and validate backtest result safety validator contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class BacktestResultSafetyValidatorContractError(ValueError):
    """Raised when backtest result safety validator contract validation fails."""


@dataclass(frozen=True)
class BacktestResultSafetyValidatorContract:
    """Machine-readable backtest result safety validator contract."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    source_contracts: dict[str, dict[str, Any]]
    validator_contract_scope: dict[str, dict[str, Any]]
    safety_check_groups: dict[str, list[dict[str, Any]]]
    prohibited_result_fields: list[str]
    prohibited_text_patterns: dict[str, list[str]]
    required_caveat_checks: dict[str, Any]
    output_location_enforcement: dict[str, Any]
    validator_result_contract: dict[str, Any]
    required_acceptance_before_validator_runtime: list[dict[str, Any]]
    phase_9a5_closure: dict[str, Any]
    recommended_next_phase: dict[str, Any]


def load_backtest_result_safety_validator_contract(
    path: str | Path,
) -> BacktestResultSafetyValidatorContract:
    """Load and validate backtest result safety validator contract YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BacktestResultSafetyValidatorContractError(
            f"backtest_result_safety_validator_contract file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BacktestResultSafetyValidatorContractError(
            f"Invalid YAML in {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise BacktestResultSafetyValidatorContractError(
            "backtest_result_safety_validator_contract YAML must be a mapping"
        )
    raw = payload.get("backtest_result_safety_validator_contract")
    if not isinstance(raw, dict):
        raise BacktestResultSafetyValidatorContractError(
            "backtest_result_safety_validator_contract YAML must contain a mapping"
        )
    contract = _contract_from_mapping({str(key): value for key, value in raw.items()})
    validate_backtest_result_safety_validator_contract(contract)
    return contract


def validate_backtest_result_safety_validator_contract(
    contract: BacktestResultSafetyValidatorContract,
) -> None:
    """Validate parsed backtest result safety validator contract."""

    if not isinstance(contract.version, int):
        raise BacktestResultSafetyValidatorContractError(
            "version must exist and be an integer"
        )
    if not contract.status:
        raise BacktestResultSafetyValidatorContractError("status must be non-empty")
    if not contract.source_contracts:
        raise BacktestResultSafetyValidatorContractError("source_contracts must exist")
    if not contract.validator_contract_scope:
        raise BacktestResultSafetyValidatorContractError(
            "validator_contract_scope must exist"
        )
    if not contract.safety_check_groups:
        raise BacktestResultSafetyValidatorContractError("safety_check_groups must exist")
    if not contract.prohibited_result_fields:
        raise BacktestResultSafetyValidatorContractError(
            "prohibited_result_fields must exist"
        )
    if not contract.prohibited_text_patterns:
        raise BacktestResultSafetyValidatorContractError(
            "prohibited_text_patterns must exist"
        )
    if not contract.required_caveat_checks:
        raise BacktestResultSafetyValidatorContractError(
            "required_caveat_checks must exist"
        )
    if not contract.output_location_enforcement:
        raise BacktestResultSafetyValidatorContractError(
            "output_location_enforcement must exist"
        )
    if not contract.validator_result_contract:
        raise BacktestResultSafetyValidatorContractError(
            "validator_result_contract must exist"
        )
    if not contract.required_acceptance_before_validator_runtime:
        raise BacktestResultSafetyValidatorContractError(
            "required_acceptance_before_validator_runtime must exist"
        )
    if str(contract.phase_9a5_closure.get("status") or "") != (
        "safety_validator_contract_design_only"
    ):
        raise BacktestResultSafetyValidatorContractError(
            "phase_9a5_closure.status must be safety_validator_contract_design_only"
        )
    if str(contract.recommended_next_phase.get("phase_id") or "") != "9A6":
        raise BacktestResultSafetyValidatorContractError(
            "recommended_next_phase.phase_id must be 9A6"
        )
    _validate_scope(contract.validator_contract_scope)
    _validate_check_groups(contract.safety_check_groups)
    _validate_prohibited_result_fields(contract.prohibited_result_fields)
    _validate_prohibited_text_patterns(contract.prohibited_text_patterns)
    _validate_required_caveat_checks(contract.required_caveat_checks)
    _validate_output_location_enforcement(contract.output_location_enforcement)
    _validate_validator_result_contract(contract.validator_result_contract)
    _validate_caveats(contract.caveats_zh)


def summarize_backtest_result_safety_validator_contract(
    contract: BacktestResultSafetyValidatorContract,
) -> dict[str, Any]:
    """Return a concise machine-readable safety validator contract summary."""

    validate_backtest_result_safety_validator_contract(contract)
    disallowed = contract.validator_contract_scope["disallowed_now"]
    output = contract.output_location_enforcement
    validator_result = contract.validator_result_contract
    next_phase = contract.recommended_next_phase
    return {
        "version": contract.version,
        "status": contract.status,
        "safety_check_group_count": len(
            contract.safety_check_groups["required_check_groups"]
        ),
        "prohibited_result_field_count": len(contract.prohibited_result_fields),
        "prohibited_text_pattern_count": sum(
            len(patterns) for patterns in contract.prohibited_text_patterns.values()
        ),
        "required_global_caveat_count": len(
            contract.required_caveat_checks["required_global_caveats_zh"]
        ),
        "validator_result_field_count": len(
            contract.validator_result_contract["required_future_validator_fields"]
        ),
        "run_validator_on_real_results_allowed": not bool(
            disallowed["run_validator_on_real_results"]
        ),
        "produce_backtest_results_allowed": not bool(disallowed["produce_backtest_results"]),
        "compute_metric_values_allowed": not bool(disallowed["compute_metric_values"]),
        "write_result_files_allowed": not bool(disallowed["write_result_files"]),
        "write_data_backtests_output_allowed": not bool(
            disallowed["write_data_backtests_output"]
        ),
        "write_public_output_allowed": not bool(disallowed["write_public_output"]),
        "create_output_directories_allowed": not bool(
            disallowed["create_output_directories"]
        ),
        "produce_allocation_allowed": not bool(disallowed["produce_allocation"]),
        "produce_trade_signal_allowed": not bool(disallowed["produce_trade_signal"]),
        "public_auto_output_allowed": bool(output["public_auto_output_allowed"]),
        "data_backtests_write_allowed_now": bool(output["data_backtests_write_allowed_now"]),
        "validator_runtime_allowed_now": bool(
            validator_result["validator_runtime_allowed_now"]
        ),
        "real_result_validation_allowed_now": bool(
            validator_result["real_result_validation_allowed_now"]
        ),
        "phase_9a5_closure_status": contract.phase_9a5_closure["status"],
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _contract_from_mapping(payload: dict[str, Any]) -> BacktestResultSafetyValidatorContract:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "source_contracts",
        "validator_contract_scope",
        "safety_check_groups",
        "prohibited_result_fields",
        "prohibited_text_patterns",
        "required_caveat_checks",
        "output_location_enforcement",
        "validator_result_contract",
        "required_acceptance_before_validator_runtime",
        "phase_9a5_closure",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise BacktestResultSafetyValidatorContractError(
            "backtest_result_safety_validator_contract missing required field(s): "
            f"{', '.join(missing)}"
        )
    return BacktestResultSafetyValidatorContract(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        source_contracts=_mapping_of_mappings(payload["source_contracts"], "source_contracts"),
        validator_contract_scope=_mapping_of_mappings(
            payload["validator_contract_scope"],
            "validator_contract_scope",
        ),
        safety_check_groups=_mapping_of_mapping_lists(
            payload["safety_check_groups"],
            "safety_check_groups",
        ),
        prohibited_result_fields=_str_list(
            payload["prohibited_result_fields"],
            "prohibited_result_fields",
        ),
        prohibited_text_patterns=_mapping_of_str_lists(
            payload["prohibited_text_patterns"],
            "prohibited_text_patterns",
        ),
        required_caveat_checks=_mapping(
            payload["required_caveat_checks"],
            "required_caveat_checks",
        ),
        output_location_enforcement=_mapping(
            payload["output_location_enforcement"],
            "output_location_enforcement",
        ),
        validator_result_contract=_mapping(
            payload["validator_result_contract"],
            "validator_result_contract",
        ),
        required_acceptance_before_validator_runtime=_list_of_mappings(
            payload["required_acceptance_before_validator_runtime"],
            "required_acceptance_before_validator_runtime",
        ),
        phase_9a5_closure=_mapping(payload["phase_9a5_closure"], "phase_9a5_closure"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_scope(scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(scope.get("disallowed_now"), "validator_contract_scope.disallowed_now")
    for field in (
        "run_validator_on_real_results",
        "produce_backtest_results",
        "compute_metric_values",
        "write_result_files",
        "write_data_backtests_output",
        "write_public_output",
        "create_output_directories",
        "produce_allocation",
        "produce_trade_signal",
    ):
        if disallowed.get(field) is not True:
            raise BacktestResultSafetyValidatorContractError(
                f"validator_contract_scope.disallowed_now.{field} must be true"
            )


def _validate_check_groups(groups: dict[str, list[dict[str, Any]]]) -> None:
    required_groups = groups.get("required_check_groups")
    if not required_groups:
        raise BacktestResultSafetyValidatorContractError(
            "safety_check_groups.required_check_groups must exist"
        )
    group_ids = {str(group.get("check_group_id") or "") for group in required_groups}
    required = {
        "prohibited_field_checks",
        "prohibited_text_checks",
        "required_caveat_checks",
        "caveat_visibility_checks",
        "output_location_checks",
        "metadata_caveat_checks",
        "scenario_specific_caveat_checks",
        "no_live_decision_checks",
    }
    missing = sorted(required - group_ids)
    if missing:
        raise BacktestResultSafetyValidatorContractError(
            f"safety_check_groups.required_check_groups missing group(s): {', '.join(missing)}"
        )


def _validate_prohibited_result_fields(fields: list[str]) -> None:
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
        raise BacktestResultSafetyValidatorContractError(
            f"prohibited_result_fields missing field(s): {', '.join(missing)}"
        )


def _validate_prohibited_text_patterns(patterns_by_language: dict[str, list[str]]) -> None:
    patterns = {pattern for values in patterns_by_language.values() for pattern in values}
    required = {
        "目前建議",
        "建議買進",
        "建議賣出",
        "買進訊號",
        "賣出訊號",
        "target weight",
        "investment advice",
    }
    missing = sorted(required - patterns)
    if missing:
        raise BacktestResultSafetyValidatorContractError(
            f"prohibited_text_patterns missing pattern(s): {', '.join(missing)}"
        )


def _validate_required_caveat_checks(checks: dict[str, Any]) -> None:
    caveats = set(
        _str_list(
            checks.get("required_global_caveats_zh"),
            "required_caveat_checks.required_global_caveats_zh",
        )
    )
    required = {
        "backtest-only，不是目前配置建議。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }
    missing = sorted(required - caveats)
    if missing:
        raise BacktestResultSafetyValidatorContractError(
            "required_caveat_checks.required_global_caveats_zh missing caveat(s): "
            f"{', '.join(missing)}"
        )
    if checks.get("caveats_visible_before_metrics_required") is not True:
        raise BacktestResultSafetyValidatorContractError(
            "required_caveat_checks.caveats_visible_before_metrics_required must be true"
        )


def _validate_output_location_enforcement(enforcement: dict[str, Any]) -> None:
    for field in (
        "public_auto_output_allowed",
        "github_pages_auto_output_allowed",
        "dashboard_auto_output_allowed",
        "data_backtests_write_allowed_now",
        "output_directory_creation_allowed_now",
    ):
        if enforcement.get(field) is not False:
            raise BacktestResultSafetyValidatorContractError(
                f"output_location_enforcement.{field} must be false"
            )


def _validate_validator_result_contract(contract: dict[str, Any]) -> None:
    if contract.get("validator_runtime_allowed_now") is not False:
        raise BacktestResultSafetyValidatorContractError(
            "validator_result_contract.validator_runtime_allowed_now must be false"
        )
    if contract.get("real_result_validation_allowed_now") is not False:
        raise BacktestResultSafetyValidatorContractError(
            "validator_result_contract.real_result_validation_allowed_now must be false"
        )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise BacktestResultSafetyValidatorContractError(
            "caveats_zh must include 不構成投資建議"
        )


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BacktestResultSafetyValidatorContractError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise BacktestResultSafetyValidatorContractError(
                f"{field}.{key} must be a mapping"
            )
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _mapping_of_mapping_lists(value: Any, field: str) -> dict[str, list[dict[str, Any]]]:
    mapping = _mapping(value, field)
    return {key: _list_of_mappings(raw, f"{field}.{key}") for key, raw in mapping.items()}


def _mapping_of_str_lists(value: Any, field: str) -> dict[str, list[str]]:
    mapping = _mapping(value, field)
    return {key: _str_list(raw, f"{field}.{key}") for key, raw in mapping.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BacktestResultSafetyValidatorContractError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise BacktestResultSafetyValidatorContractError(
                f"{field}[{index}] must be a mapping"
            )
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BacktestResultSafetyValidatorContractError(
            f"{field} must be a non-empty list"
        )
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise BacktestResultSafetyValidatorContractError(
            f"{field} must not contain empty items"
        )
    return result
