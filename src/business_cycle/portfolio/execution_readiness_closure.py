"""Load and validate real backtest execution readiness closures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class RealBacktestExecutionReadinessClosureError(ValueError):
    """Raised when real backtest execution readiness closure validation fails."""


@dataclass(frozen=True)
class RealBacktestExecutionReadinessClosure:
    """Machine-readable real backtest execution readiness closure."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    source_artifacts: dict[str, dict[str, Any]]
    required_validator_commands: list[dict[str, Any]]
    readiness_scope: dict[str, dict[str, Any]]
    source_artifact_readiness: dict[str, Any]
    safety_boundary_summary: dict[str, Any]
    phase_9b_entry_conditions: dict[str, Any]
    remaining_blockers_for_output_writing: dict[str, dict[str, Any]]
    phase_9a8_closure: dict[str, Any]
    recommended_next_phase: dict[str, Any]


def load_real_backtest_execution_readiness_closure(
    path: str | Path,
) -> RealBacktestExecutionReadinessClosure:
    """Load and validate real backtest execution readiness closure YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise RealBacktestExecutionReadinessClosureError(
            f"real_backtest_execution_readiness_closure file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RealBacktestExecutionReadinessClosureError(
            f"Invalid YAML in {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise RealBacktestExecutionReadinessClosureError(
            "real_backtest_execution_readiness_closure YAML must be a mapping"
        )
    raw = payload.get("real_backtest_execution_readiness_closure")
    if not isinstance(raw, dict):
        raise RealBacktestExecutionReadinessClosureError(
            "real_backtest_execution_readiness_closure YAML must contain a mapping"
        )
    closure = _closure_from_mapping({str(key): value for key, value in raw.items()})
    validate_real_backtest_execution_readiness_closure(closure)
    return closure


def validate_real_backtest_execution_readiness_closure(
    closure: RealBacktestExecutionReadinessClosure,
) -> None:
    """Validate parsed real backtest execution readiness closure."""

    if not isinstance(closure.version, int):
        raise RealBacktestExecutionReadinessClosureError(
            "version must exist and be an integer"
        )
    if not closure.status:
        raise RealBacktestExecutionReadinessClosureError("status must be non-empty")
    if not closure.source_artifacts:
        raise RealBacktestExecutionReadinessClosureError("source_artifacts must exist")
    if not closure.required_validator_commands:
        raise RealBacktestExecutionReadinessClosureError(
            "required_validator_commands must exist"
        )
    if not closure.readiness_scope:
        raise RealBacktestExecutionReadinessClosureError("readiness_scope must exist")
    if not closure.source_artifact_readiness:
        raise RealBacktestExecutionReadinessClosureError(
            "source_artifact_readiness must exist"
        )
    if not closure.safety_boundary_summary:
        raise RealBacktestExecutionReadinessClosureError(
            "safety_boundary_summary must exist"
        )
    if not closure.phase_9b_entry_conditions:
        raise RealBacktestExecutionReadinessClosureError(
            "phase_9b_entry_conditions must exist"
        )
    if not closure.remaining_blockers_for_output_writing:
        raise RealBacktestExecutionReadinessClosureError(
            "remaining_blockers_for_output_writing must exist"
        )
    if str(closure.phase_9a8_closure.get("status") or "") != (
        "ready_for_controlled_9b_prototype"
    ):
        raise RealBacktestExecutionReadinessClosureError(
            "phase_9a8_closure.status must be ready_for_controlled_9b_prototype"
        )
    if str(closure.recommended_next_phase.get("phase_id") or "") != "9B":
        raise RealBacktestExecutionReadinessClosureError(
            "recommended_next_phase.phase_id must be 9B"
        )
    _validate_source_artifact_readiness(closure.source_artifact_readiness)
    _validate_readiness_scope(closure.readiness_scope)
    _validate_safety_boundaries(closure.safety_boundary_summary)
    _validate_phase_9b_entry_conditions(closure.phase_9b_entry_conditions)
    _validate_remaining_blockers(closure.remaining_blockers_for_output_writing)
    _validate_caveats(closure.caveats_zh)


def summarize_real_backtest_execution_readiness_closure(
    closure: RealBacktestExecutionReadinessClosure,
) -> dict[str, Any]:
    """Return a concise machine-readable readiness closure summary."""

    validate_real_backtest_execution_readiness_closure(closure)
    safety = closure.safety_boundary_summary
    entry = closure.phase_9b_entry_conditions
    next_phase = closure.recommended_next_phase
    return {
        "version": closure.version,
        "status": closure.status,
        "source_artifact_count": len(closure.source_artifacts),
        "validator_command_count": len(closure.required_validator_commands),
        "remaining_output_write_blocker_count": _active_blocker_count(
            closure.remaining_blockers_for_output_writing
        ),
        "phase_9a_contract_stack_complete": bool(
            closure.source_artifact_readiness["phase_9a_contract_stack_complete"]
        ),
        "real_backtest_execution_allowed_now": bool(
            safety["real_backtest_execution_allowed_now"]
        ),
        "engine_runtime_allowed_now": bool(safety["engine_runtime_allowed_now"]),
        "writer_runtime_allowed_now": bool(safety["writer_runtime_allowed_now"]),
        "real_result_validator_runtime_allowed_now": bool(
            safety["real_result_validator_runtime_allowed_now"]
        ),
        "metric_computation_allowed_now": bool(
            safety["metric_computation_allowed_now"]
        ),
        "result_generation_allowed_now": bool(safety["result_generation_allowed_now"]),
        "result_file_write_allowed_now": bool(safety["result_file_write_allowed_now"]),
        "output_directory_creation_allowed_now": bool(
            safety["output_directory_creation_allowed_now"]
        ),
        "data_backtests_write_allowed_now": bool(
            safety["data_backtests_write_allowed_now"]
        ),
        "public_write_allowed_now": bool(safety["public_write_allowed_now"]),
        "allocation_output_allowed_now": bool(safety["allocation_output_allowed_now"]),
        "trade_signal_output_allowed_now": bool(
            safety["trade_signal_output_allowed_now"]
        ),
        "live_recommendation_allowed_now": bool(
            safety["live_recommendation_allowed_now"]
        ),
        "controlled_9b_prototype_entry_allowed": bool(
            entry["controlled_real_backtest_prototype_entry_allowed_after_closure"]
        ),
        "default_9b_output_write_allowed": bool(entry["default_output_write_allowed"]),
        "phase_9a8_closure_status": closure.phase_9a8_closure["status"],
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _closure_from_mapping(payload: dict[str, Any]) -> RealBacktestExecutionReadinessClosure:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "source_artifacts",
        "required_validator_commands",
        "readiness_scope",
        "source_artifact_readiness",
        "safety_boundary_summary",
        "phase_9b_entry_conditions",
        "remaining_blockers_for_output_writing",
        "phase_9a8_closure",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise RealBacktestExecutionReadinessClosureError(
            "real_backtest_execution_readiness_closure missing required field(s): "
            f"{', '.join(missing)}"
        )
    return RealBacktestExecutionReadinessClosure(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        source_artifacts=_mapping_of_mappings(payload["source_artifacts"], "source_artifacts"),
        required_validator_commands=_list_of_mappings(
            payload["required_validator_commands"],
            "required_validator_commands",
        ),
        readiness_scope=_mapping_of_mappings(
            payload["readiness_scope"],
            "readiness_scope",
        ),
        source_artifact_readiness=_mapping(
            payload["source_artifact_readiness"],
            "source_artifact_readiness",
        ),
        safety_boundary_summary=_mapping(
            payload["safety_boundary_summary"],
            "safety_boundary_summary",
        ),
        phase_9b_entry_conditions=_mapping(
            payload["phase_9b_entry_conditions"],
            "phase_9b_entry_conditions",
        ),
        remaining_blockers_for_output_writing=_mapping_of_mappings(
            payload["remaining_blockers_for_output_writing"],
            "remaining_blockers_for_output_writing",
        ),
        phase_9a8_closure=_mapping(payload["phase_9a8_closure"], "phase_9a8_closure"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_source_artifact_readiness(readiness: dict[str, Any]) -> None:
    if readiness.get("required_artifact_count") != 10:
        raise RealBacktestExecutionReadinessClosureError(
            "source_artifact_readiness.required_artifact_count must be 10"
        )
    for field in (
        "all_required_artifacts_present",
        "all_required_artifacts_validated",
        "phase_9a_contract_stack_complete",
    ):
        if readiness.get(field) is not True:
            raise RealBacktestExecutionReadinessClosureError(
                f"source_artifact_readiness.{field} must be true"
            )


def _validate_readiness_scope(scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(scope.get("disallowed_now"), "readiness_scope.disallowed_now")
    for field in (
        "execute_backtest",
        "implement_engine_runtime",
        "implement_writer_runtime",
        "implement_real_result_validator_runtime",
        "compute_metric_values",
        "produce_backtest_results",
        "write_result_files",
        "create_output_directories",
        "write_data_backtests_output",
        "write_public_output",
        "produce_allocation",
        "produce_trade_signal",
    ):
        if disallowed.get(field) is not True:
            raise RealBacktestExecutionReadinessClosureError(
                f"readiness_scope.disallowed_now.{field} must be true"
            )


def _validate_safety_boundaries(safety: dict[str, Any]) -> None:
    for field in (
        "real_backtest_execution_allowed_now",
        "engine_runtime_allowed_now",
        "writer_runtime_allowed_now",
        "real_result_validator_runtime_allowed_now",
        "metric_computation_allowed_now",
        "result_generation_allowed_now",
        "result_file_write_allowed_now",
        "output_directory_creation_allowed_now",
        "data_backtests_write_allowed_now",
        "public_write_allowed_now",
        "allocation_output_allowed_now",
        "trade_signal_output_allowed_now",
        "live_recommendation_allowed_now",
    ):
        if safety.get(field) is not False:
            raise RealBacktestExecutionReadinessClosureError(
                f"safety_boundary_summary.{field} must be false"
            )


def _validate_phase_9b_entry_conditions(entry: dict[str, Any]) -> None:
    if entry.get("controlled_real_backtest_prototype_entry_allowed_after_closure") is not True:
        raise RealBacktestExecutionReadinessClosureError(
            "phase_9b_entry_conditions."
            "controlled_real_backtest_prototype_entry_allowed_after_closure must be true"
        )
    for field in (
        "default_output_write_allowed",
        "default_public_output_allowed",
        "default_allocation_output_allowed",
        "default_trade_signal_allowed",
    ):
        if entry.get(field) is not False:
            raise RealBacktestExecutionReadinessClosureError(
                f"phase_9b_entry_conditions.{field} must be false"
            )
    scope = str(entry.get("recommended_9b_initial_scope_zh") or "")
    for required in (
        "controlled in-memory real backtest prototype",
        "不得自動寫檔",
        "不接 dashboard",
        "不產生 live allocation 或 trade signal",
    ):
        if required not in scope:
            raise RealBacktestExecutionReadinessClosureError(
                "phase_9b_entry_conditions.recommended_9b_initial_scope_zh "
                f"must include {required}"
            )


def _validate_remaining_blockers(blockers: dict[str, dict[str, Any]]) -> None:
    if _active_blocker_count(blockers) < 4:
        raise RealBacktestExecutionReadinessClosureError(
            "remaining_blockers_for_output_writing must include at least 4 active blockers"
        )


def _active_blocker_count(blockers: dict[str, dict[str, Any]]) -> int:
    return sum(1 for blocker in blockers.values() if blocker.get("active") is True)


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise RealBacktestExecutionReadinessClosureError(
            "caveats_zh must include 不構成投資建議"
        )


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RealBacktestExecutionReadinessClosureError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise RealBacktestExecutionReadinessClosureError(
                f"{field}.{key} must be a mapping"
            )
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RealBacktestExecutionReadinessClosureError(
            f"{field} must be a non-empty list"
        )
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise RealBacktestExecutionReadinessClosureError(
                f"{field}[{index}] must be a mapping"
            )
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RealBacktestExecutionReadinessClosureError(
            f"{field} must be a non-empty list"
        )
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise RealBacktestExecutionReadinessClosureError(
            f"{field} must not contain empty items"
        )
    return result
