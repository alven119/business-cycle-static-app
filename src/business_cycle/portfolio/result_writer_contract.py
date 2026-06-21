"""Load and validate backtest result writer contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class BacktestResultWriterContractError(ValueError):
    """Raised when backtest result writer contract validation fails."""


@dataclass(frozen=True)
class BacktestResultWriterContract:
    """Machine-readable backtest result writer contract."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    source_contracts: dict[str, dict[str, Any]]
    writer_contract_scope: dict[str, dict[str, Any]]
    future_writer_trigger_policy: dict[str, Any]
    allowed_future_output_paths: dict[str, dict[str, Any]]
    prohibited_write_locations: list[str]
    required_pre_write_validations: list[dict[str, Any]]
    writer_status_contract: dict[str, Any]
    prohibited_result_fields_for_writer: list[str]
    required_writer_caveats_zh: list[str]
    phase_9a7_closure: dict[str, Any]
    recommended_next_phase: dict[str, Any]


def load_backtest_result_writer_contract(path: str | Path) -> BacktestResultWriterContract:
    """Load and validate backtest result writer contract YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BacktestResultWriterContractError(
            f"backtest_result_writer_contract file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BacktestResultWriterContractError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BacktestResultWriterContractError(
            "backtest_result_writer_contract YAML must be a mapping"
        )
    raw = payload.get("backtest_result_writer_contract")
    if not isinstance(raw, dict):
        raise BacktestResultWriterContractError(
            "backtest_result_writer_contract YAML must contain a mapping"
        )
    contract = _contract_from_mapping({str(key): value for key, value in raw.items()})
    validate_backtest_result_writer_contract(contract)
    return contract


def validate_backtest_result_writer_contract(
    contract: BacktestResultWriterContract,
) -> None:
    """Validate parsed backtest result writer contract."""

    if not isinstance(contract.version, int):
        raise BacktestResultWriterContractError("version must exist and be an integer")
    if not contract.status:
        raise BacktestResultWriterContractError("status must be non-empty")
    if not contract.source_contracts:
        raise BacktestResultWriterContractError("source_contracts must exist")
    if not contract.writer_contract_scope:
        raise BacktestResultWriterContractError("writer_contract_scope must exist")
    if not contract.future_writer_trigger_policy:
        raise BacktestResultWriterContractError("future_writer_trigger_policy must exist")
    if not contract.allowed_future_output_paths:
        raise BacktestResultWriterContractError("allowed_future_output_paths must exist")
    if not contract.prohibited_write_locations:
        raise BacktestResultWriterContractError("prohibited_write_locations must exist")
    if not contract.required_pre_write_validations:
        raise BacktestResultWriterContractError(
            "required_pre_write_validations must exist"
        )
    if not contract.writer_status_contract:
        raise BacktestResultWriterContractError("writer_status_contract must exist")
    if not contract.prohibited_result_fields_for_writer:
        raise BacktestResultWriterContractError(
            "prohibited_result_fields_for_writer must exist"
        )
    if not contract.required_writer_caveats_zh:
        raise BacktestResultWriterContractError("required_writer_caveats_zh must exist")
    if str(contract.phase_9a7_closure.get("status") or "") != (
        "writer_contract_design_only"
    ):
        raise BacktestResultWriterContractError(
            "phase_9a7_closure.status must be writer_contract_design_only"
        )
    if str(contract.recommended_next_phase.get("phase_id") or "") != "9A8":
        raise BacktestResultWriterContractError(
            "recommended_next_phase.phase_id must be 9A8"
        )
    _validate_scope(contract.writer_contract_scope)
    _validate_trigger_policy(contract.future_writer_trigger_policy)
    _validate_future_output_path(contract.allowed_future_output_paths)
    _validate_prohibited_write_locations(contract.prohibited_write_locations)
    _validate_pre_write_validations(contract.required_pre_write_validations)
    _validate_writer_status_contract(contract.writer_status_contract)
    _validate_prohibited_result_fields(contract.prohibited_result_fields_for_writer)
    _validate_required_caveats(contract.required_writer_caveats_zh)
    _validate_caveats(contract.caveats_zh)


def summarize_backtest_result_writer_contract(
    contract: BacktestResultWriterContract,
) -> dict[str, Any]:
    """Return a concise machine-readable writer contract summary."""

    validate_backtest_result_writer_contract(contract)
    disallowed = contract.writer_contract_scope["disallowed_now"]
    trigger = contract.future_writer_trigger_policy
    status = contract.writer_status_contract
    next_phase = contract.recommended_next_phase
    return {
        "version": contract.version,
        "status": contract.status,
        "prohibited_write_location_count": len(contract.prohibited_write_locations),
        "pre_write_validation_count": len(contract.required_pre_write_validations),
        "writer_status_field_count": len(status["required_future_writer_fields"]),
        "prohibited_result_field_count": len(
            contract.prohibited_result_fields_for_writer
        ),
        "explicit_user_command_required": bool(
            trigger["explicit_user_command_required"]
        ),
        "automatic_write_allowed": bool(trigger["automatic_write_allowed"]),
        "implement_writer_runtime_allowed": not bool(
            disallowed["implement_writer_runtime"]
        ),
        "write_result_files_allowed": not bool(disallowed["write_result_files"]),
        "create_output_directories_allowed": not bool(
            disallowed["create_output_directories"]
        ),
        "write_data_backtests_output_allowed": not bool(
            disallowed["write_data_backtests_output"]
        ),
        "write_public_output_allowed": not bool(disallowed["write_public_output"]),
        "write_docs_output_allowed": not bool(disallowed["write_docs_output"]),
        "write_dashboard_output_allowed": not bool(disallowed["write_dashboard_output"]),
        "write_github_pages_output_allowed": not bool(
            disallowed["write_github_pages_output"]
        ),
        "execute_backtest_allowed": not bool(disallowed["execute_backtest"]),
        "compute_metric_values_allowed": not bool(disallowed["compute_metric_values"]),
        "produce_allocation_allowed": not bool(disallowed["produce_allocation"]),
        "produce_trade_signal_allowed": not bool(disallowed["produce_trade_signal"]),
        "writer_runtime_allowed_now": bool(status["writer_runtime_allowed_now"]),
        "result_file_write_allowed_now": bool(status["result_file_write_allowed_now"]),
        "output_directory_creation_allowed_now": bool(
            status["output_directory_creation_allowed_now"]
        ),
        "data_backtests_write_allowed_now": bool(
            status["data_backtests_write_allowed_now"]
        ),
        "public_write_allowed_now": bool(status["public_write_allowed_now"]),
        "phase_9a7_closure_status": contract.phase_9a7_closure["status"],
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _contract_from_mapping(payload: dict[str, Any]) -> BacktestResultWriterContract:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "source_contracts",
        "writer_contract_scope",
        "future_writer_trigger_policy",
        "allowed_future_output_paths",
        "prohibited_write_locations",
        "required_pre_write_validations",
        "writer_status_contract",
        "prohibited_result_fields_for_writer",
        "required_writer_caveats_zh",
        "phase_9a7_closure",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise BacktestResultWriterContractError(
            "backtest_result_writer_contract missing required field(s): "
            f"{', '.join(missing)}"
        )
    return BacktestResultWriterContract(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        source_contracts=_mapping_of_mappings(payload["source_contracts"], "source_contracts"),
        writer_contract_scope=_mapping_of_mappings(
            payload["writer_contract_scope"],
            "writer_contract_scope",
        ),
        future_writer_trigger_policy=_mapping(
            payload["future_writer_trigger_policy"],
            "future_writer_trigger_policy",
        ),
        allowed_future_output_paths=_mapping_of_mappings(
            payload["allowed_future_output_paths"],
            "allowed_future_output_paths",
        ),
        prohibited_write_locations=_str_list(
            payload["prohibited_write_locations"],
            "prohibited_write_locations",
        ),
        required_pre_write_validations=_list_of_mappings(
            payload["required_pre_write_validations"],
            "required_pre_write_validations",
        ),
        writer_status_contract=_mapping(
            payload["writer_status_contract"],
            "writer_status_contract",
        ),
        prohibited_result_fields_for_writer=_str_list(
            payload["prohibited_result_fields_for_writer"],
            "prohibited_result_fields_for_writer",
        ),
        required_writer_caveats_zh=_str_list(
            payload["required_writer_caveats_zh"],
            "required_writer_caveats_zh",
        ),
        phase_9a7_closure=_mapping(payload["phase_9a7_closure"], "phase_9a7_closure"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_scope(scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(scope.get("disallowed_now"), "writer_contract_scope.disallowed_now")
    for field in (
        "implement_writer_runtime",
        "write_result_files",
        "create_output_directories",
        "write_data_backtests_output",
        "write_public_output",
        "write_docs_output",
        "write_dashboard_output",
        "write_github_pages_output",
        "execute_backtest",
        "compute_metric_values",
        "produce_allocation",
        "produce_trade_signal",
    ):
        if disallowed.get(field) is not True:
            raise BacktestResultWriterContractError(
                f"writer_contract_scope.disallowed_now.{field} must be true"
            )


def _validate_trigger_policy(policy: dict[str, Any]) -> None:
    if policy.get("explicit_user_command_required") is not True:
        raise BacktestResultWriterContractError(
            "future_writer_trigger_policy.explicit_user_command_required must be true"
        )
    for field in (
        "automatic_write_allowed",
        "scheduled_write_allowed",
        "dashboard_triggered_write_allowed",
        "github_pages_triggered_write_allowed",
        "ci_auto_write_allowed",
    ):
        if policy.get(field) is not False:
            raise BacktestResultWriterContractError(
                f"future_writer_trigger_policy.{field} must be false"
            )


def _validate_future_output_path(paths: dict[str, dict[str, Any]]) -> None:
    controlled = _mapping(
        paths.get("controlled_research_path"),
        "allowed_future_output_paths.controlled_research_path",
    )
    if controlled.get("path") != "data/backtests/research":
        raise BacktestResultWriterContractError(
            "allowed_future_output_paths.controlled_research_path.path "
            "must be data/backtests/research"
        )
    for field in (
        "allowed_only_after_future_writer_runtime_phase",
        "requires_explicit_user_command",
        "requires_safety_validator_pass",
        "requires_caveat_policy_pass",
        "requires_output_location_policy_pass",
    ):
        if controlled.get(field) is not True:
            raise BacktestResultWriterContractError(
                "allowed_future_output_paths.controlled_research_path."
                f"{field} must be true"
            )
    for field in ("auto_publication_allowed", "git_tracking_allowed"):
        if controlled.get(field) is not False:
            raise BacktestResultWriterContractError(
                "allowed_future_output_paths.controlled_research_path."
                f"{field} must be false"
            )


def _validate_prohibited_write_locations(locations: list[str]) -> None:
    required = {
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
    }
    missing = sorted(required - set(locations))
    if missing:
        raise BacktestResultWriterContractError(
            f"prohibited_write_locations missing location(s): {', '.join(missing)}"
        )


def _validate_pre_write_validations(validations: list[dict[str, Any]]) -> None:
    validation_ids = {str(item.get("validation_id") or "") for item in validations}
    required = {
        "result_safety_validator_runtime_available",
        "result_safety_validation_passed",
        "explicit_user_command_present",
        "no_public_auto_output",
        "no_live_allocation_or_trade_signal",
    }
    missing = sorted(required - validation_ids)
    if missing:
        raise BacktestResultWriterContractError(
            "required_pre_write_validations missing validation(s): "
            f"{', '.join(missing)}"
        )


def _validate_writer_status_contract(status: dict[str, Any]) -> None:
    for field in (
        "writer_runtime_allowed_now",
        "result_file_write_allowed_now",
        "output_directory_creation_allowed_now",
        "data_backtests_write_allowed_now",
        "public_write_allowed_now",
        "docs_write_allowed_now",
        "dashboard_write_allowed_now",
        "github_pages_write_allowed_now",
    ):
        if status.get(field) is not False:
            raise BacktestResultWriterContractError(
                f"writer_status_contract.{field} must be false"
            )
    _str_list(
        status.get("required_future_writer_fields"),
        "writer_status_contract.required_future_writer_fields",
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
        raise BacktestResultWriterContractError(
            "prohibited_result_fields_for_writer missing field(s): "
            f"{', '.join(missing)}"
        )


def _validate_required_caveats(caveats: list[str]) -> None:
    required = {
        "backtest-only，不是目前配置建議。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }
    missing = sorted(required - set(caveats))
    if missing:
        raise BacktestResultWriterContractError(
            f"required_writer_caveats_zh missing caveat(s): {', '.join(missing)}"
        )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise BacktestResultWriterContractError(
            "caveats_zh must include 不構成投資建議"
        )


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BacktestResultWriterContractError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise BacktestResultWriterContractError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BacktestResultWriterContractError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise BacktestResultWriterContractError(
                f"{field}[{index}] must be a mapping"
            )
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BacktestResultWriterContractError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise BacktestResultWriterContractError(f"{field} must not contain empty items")
    return result
