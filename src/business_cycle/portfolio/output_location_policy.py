"""Load and validate backtest output location policies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class BacktestOutputLocationPolicyError(ValueError):
    """Raised when backtest output location policy validation fails."""


@dataclass(frozen=True)
class BacktestOutputLocationPolicy:
    """Machine-readable backtest output location policy."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    source_contracts: dict[str, dict[str, Any]]
    location_policy_scope: dict[str, dict[str, Any]]
    future_controlled_research_paths: dict[str, list[dict[str, Any]]]
    prohibited_auto_write_locations: list[str]
    prohibited_auto_publication: dict[str, Any]
    write_preconditions_before_any_result_file: list[dict[str, Any]]
    output_file_policy: dict[str, Any]
    required_safety_dependencies: dict[str, dict[str, Any]]
    prohibited_result_fields_for_any_written_output: list[str]
    phase_9a3_closure: dict[str, Any]
    recommended_next_phase: dict[str, Any]


def load_backtest_output_location_policy(path: str | Path) -> BacktestOutputLocationPolicy:
    """Load and validate backtest output location policy YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BacktestOutputLocationPolicyError(
            f"backtest_output_location_policy file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BacktestOutputLocationPolicyError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BacktestOutputLocationPolicyError(
            "backtest_output_location_policy YAML must be a mapping"
        )
    raw = payload.get("backtest_output_location_policy")
    if not isinstance(raw, dict):
        raise BacktestOutputLocationPolicyError(
            "backtest_output_location_policy YAML must contain a mapping"
        )
    policy = _policy_from_mapping({str(key): value for key, value in raw.items()})
    validate_backtest_output_location_policy(policy)
    return policy


def validate_backtest_output_location_policy(policy: BacktestOutputLocationPolicy) -> None:
    """Validate parsed backtest output location policy."""

    if not isinstance(policy.version, int):
        raise BacktestOutputLocationPolicyError("version must exist and be an integer")
    if not policy.status:
        raise BacktestOutputLocationPolicyError("status must be non-empty")
    if not policy.source_contracts:
        raise BacktestOutputLocationPolicyError("source_contracts must exist")
    if not policy.location_policy_scope:
        raise BacktestOutputLocationPolicyError("location_policy_scope must exist")
    if not policy.future_controlled_research_paths:
        raise BacktestOutputLocationPolicyError("future_controlled_research_paths must exist")
    if not policy.prohibited_auto_write_locations:
        raise BacktestOutputLocationPolicyError("prohibited_auto_write_locations must exist")
    if not policy.prohibited_auto_publication:
        raise BacktestOutputLocationPolicyError("prohibited_auto_publication must exist")
    if not policy.write_preconditions_before_any_result_file:
        raise BacktestOutputLocationPolicyError(
            "write_preconditions_before_any_result_file must exist"
        )
    if not policy.output_file_policy:
        raise BacktestOutputLocationPolicyError("output_file_policy must exist")
    if not policy.required_safety_dependencies:
        raise BacktestOutputLocationPolicyError("required_safety_dependencies must exist")
    if not policy.prohibited_result_fields_for_any_written_output:
        raise BacktestOutputLocationPolicyError(
            "prohibited_result_fields_for_any_written_output must exist"
        )
    if str(policy.phase_9a3_closure.get("status") or "") != (
        "output_location_policy_design_only"
    ):
        raise BacktestOutputLocationPolicyError(
            "phase_9a3_closure.status must be output_location_policy_design_only"
        )
    if str(policy.recommended_next_phase.get("phase_id") or "") != "9A4":
        raise BacktestOutputLocationPolicyError("recommended_next_phase.phase_id must be 9A4")
    _validate_scope(policy.location_policy_scope)
    _validate_future_research_paths(policy.future_controlled_research_paths)
    _validate_prohibited_locations(policy.prohibited_auto_write_locations)
    _validate_output_file_policy(policy.output_file_policy)
    _validate_write_preconditions(policy.write_preconditions_before_any_result_file)
    _validate_safety_dependencies(policy.required_safety_dependencies)
    _validate_prohibited_result_fields(policy.prohibited_result_fields_for_any_written_output)
    _validate_caveats(policy.caveats_zh)


def summarize_backtest_output_location_policy(
    policy: BacktestOutputLocationPolicy,
) -> dict[str, Any]:
    """Return a concise machine-readable output location policy summary."""

    validate_backtest_output_location_policy(policy)
    disallowed = policy.location_policy_scope["disallowed_now"]
    output_policy = policy.output_file_policy
    next_phase = policy.recommended_next_phase
    future_paths = policy.future_controlled_research_paths[
        "allowed_only_after_future_writer_phase"
    ]
    return {
        "version": policy.version,
        "status": policy.status,
        "future_controlled_research_path_count": len(future_paths),
        "prohibited_auto_write_location_count": len(policy.prohibited_auto_write_locations),
        "write_precondition_count": len(policy.write_preconditions_before_any_result_file),
        "prohibited_result_field_count": len(
            policy.prohibited_result_fields_for_any_written_output
        ),
        "write_result_files_allowed": not bool(disallowed["write_result_files"]),
        "write_data_backtests_output_allowed": not bool(
            disallowed["write_data_backtests_output"]
        ),
        "write_public_output_allowed": not bool(disallowed["write_public_output"]),
        "create_output_directories_allowed": not bool(
            disallowed["create_output_directories"]
        ),
        "execute_backtest_allowed": not bool(disallowed["execute_backtest"]),
        "compute_metric_values_allowed": not bool(disallowed["compute_metric_values"]),
        "produce_backtest_results_allowed": not bool(disallowed["produce_backtest_results"]),
        "produce_allocation_allowed": not bool(disallowed["produce_allocation"]),
        "produce_trade_signal_allowed": not bool(disallowed["produce_trade_signal"]),
        "default_write_allowed_now": bool(output_policy["default_write_allowed_now"]),
        "public_sync_allowed_now": bool(output_policy["public_sync_allowed_now"]),
        "git_track_result_files_allowed_now": bool(
            output_policy["git_track_result_files_allowed_now"]
        ),
        "phase_9a3_closure_status": policy.phase_9a3_closure["status"],
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _policy_from_mapping(payload: dict[str, Any]) -> BacktestOutputLocationPolicy:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "source_contracts",
        "location_policy_scope",
        "future_controlled_research_paths",
        "prohibited_auto_write_locations",
        "prohibited_auto_publication",
        "write_preconditions_before_any_result_file",
        "output_file_policy",
        "required_safety_dependencies",
        "prohibited_result_fields_for_any_written_output",
        "phase_9a3_closure",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise BacktestOutputLocationPolicyError(
            "backtest_output_location_policy missing required field(s): "
            f"{', '.join(missing)}"
        )
    return BacktestOutputLocationPolicy(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        source_contracts=_mapping_of_mappings(payload["source_contracts"], "source_contracts"),
        location_policy_scope=_mapping_of_mappings(
            payload["location_policy_scope"],
            "location_policy_scope",
        ),
        future_controlled_research_paths=_mapping_of_mapping_lists(
            payload["future_controlled_research_paths"],
            "future_controlled_research_paths",
        ),
        prohibited_auto_write_locations=_str_list(
            payload["prohibited_auto_write_locations"],
            "prohibited_auto_write_locations",
        ),
        prohibited_auto_publication=_mapping(
            payload["prohibited_auto_publication"],
            "prohibited_auto_publication",
        ),
        write_preconditions_before_any_result_file=_list_of_mappings(
            payload["write_preconditions_before_any_result_file"],
            "write_preconditions_before_any_result_file",
        ),
        output_file_policy=_mapping(payload["output_file_policy"], "output_file_policy"),
        required_safety_dependencies=_mapping_of_mappings(
            payload["required_safety_dependencies"],
            "required_safety_dependencies",
        ),
        prohibited_result_fields_for_any_written_output=_str_list(
            payload["prohibited_result_fields_for_any_written_output"],
            "prohibited_result_fields_for_any_written_output",
        ),
        phase_9a3_closure=_mapping(payload["phase_9a3_closure"], "phase_9a3_closure"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_scope(scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(scope.get("disallowed_now"), "location_policy_scope.disallowed_now")
    for field in (
        "write_result_files",
        "write_data_backtests_output",
        "write_public_output",
        "create_output_directories",
        "execute_backtest",
        "compute_metric_values",
        "produce_backtest_results",
        "produce_allocation",
        "produce_trade_signal",
    ):
        if disallowed.get(field) is not True:
            raise BacktestOutputLocationPolicyError(
                f"location_policy_scope.disallowed_now.{field} must be true"
            )


def _validate_future_research_paths(paths_by_policy: dict[str, list[dict[str, Any]]]) -> None:
    paths = paths_by_policy.get("allowed_only_after_future_writer_phase")
    if not paths:
        raise BacktestOutputLocationPolicyError(
            "future_controlled_research_paths.allowed_only_after_future_writer_phase "
            "must exist"
        )
    research_path = next(
        (item for item in paths if str(item.get("path") or "") == "data/backtests/research"),
        None,
    )
    if research_path is None:
        raise BacktestOutputLocationPolicyError(
            "future_controlled_research_paths must include data/backtests/research"
        )
    for field in (
        "auto_publication_allowed",
        "git_tracking_allowed",
    ):
        if research_path.get(field) is not False:
            raise BacktestOutputLocationPolicyError(
                f"data/backtests/research.{field} must be false"
            )
    if research_path.get("requires_explicit_user_command") is not True:
        raise BacktestOutputLocationPolicyError(
            "data/backtests/research.requires_explicit_user_command must be true"
        )


def _validate_prohibited_locations(locations: list[str]) -> None:
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
        raise BacktestOutputLocationPolicyError(
            f"prohibited_auto_write_locations missing location(s): {', '.join(missing)}"
        )


def _validate_output_file_policy(output_policy: dict[str, Any]) -> None:
    for field in (
        "default_write_allowed_now",
        "directory_creation_allowed_now",
        "public_sync_allowed_now",
        "git_track_result_files_allowed_now",
    ):
        if output_policy.get(field) is not False:
            raise BacktestOutputLocationPolicyError(f"output_file_policy.{field} must be false")


def _validate_write_preconditions(preconditions: list[dict[str, Any]]) -> None:
    target_ids = {str(item.get("target_id") or "") for item in preconditions}
    required = {
        "explicit_output_writer_phase",
        "explicit_user_command_required",
        "no_public_auto_output",
        "no_live_allocation_or_trade_signal",
    }
    missing = sorted(required - target_ids)
    if missing:
        raise BacktestOutputLocationPolicyError(
            "write_preconditions_before_any_result_file missing target_id(s): "
            f"{', '.join(missing)}"
        )


def _validate_safety_dependencies(dependencies: dict[str, dict[str, Any]]) -> None:
    required = {
        "backtest_result_safety_validator",
        "backtest_result_caveat_policy",
        "explicit_output_writer_contract",
    }
    missing = sorted(required - set(dependencies))
    if missing:
        raise BacktestOutputLocationPolicyError(
            f"required_safety_dependencies missing dependency: {', '.join(missing)}"
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
        raise BacktestOutputLocationPolicyError(
            "prohibited_result_fields_for_any_written_output missing field(s): "
            f"{', '.join(missing)}"
        )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise BacktestOutputLocationPolicyError("caveats_zh must include 不構成投資建議")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BacktestOutputLocationPolicyError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise BacktestOutputLocationPolicyError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _mapping_of_mapping_lists(value: Any, field: str) -> dict[str, list[dict[str, Any]]]:
    mapping = _mapping(value, field)
    return {key: _list_of_mappings(raw, f"{field}.{key}") for key, raw in mapping.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BacktestOutputLocationPolicyError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise BacktestOutputLocationPolicyError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BacktestOutputLocationPolicyError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise BacktestOutputLocationPolicyError(f"{field} must not contain empty items")
    return result
