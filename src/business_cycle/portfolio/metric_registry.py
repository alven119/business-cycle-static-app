"""Load and validate backtest metric formula registries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class BacktestMetricFormulaRegistryError(ValueError):
    """Raised when backtest metric formula registry validation fails."""


@dataclass(frozen=True)
class BacktestMetricFormulaRegistry:
    """Machine-readable backtest metric formula registry."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    source_contracts: dict[str, dict[str, Any]]
    registry_scope: dict[str, dict[str, Any]]
    required_series_inputs: dict[str, dict[str, Any]]
    metric_definitions: dict[str, dict[str, Any]]
    prohibited_metric_outputs_now: list[str]
    prohibited_result_fields: list[str]
    required_metric_caveats_zh: list[str]
    required_acceptance_before_metric_computation: list[dict[str, Any]]
    phase_9a2_closure: dict[str, Any]
    recommended_next_phase: dict[str, Any]


REQUIRED_METRIC_IDS = {
    "total_return",
    "annualized_return",
    "volatility",
    "max_drawdown",
    "turnover",
    "whipsaw_count",
    "false_de_risk_cost",
    "false_re_risk_cost",
    "missed_recovery_cost",
    "late_exit_cost",
    "late_reentry_cost",
}


def load_backtest_metric_formula_registry(path: str | Path) -> BacktestMetricFormulaRegistry:
    """Load and validate backtest metric formula registry YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BacktestMetricFormulaRegistryError(
            f"backtest_metric_formula_registry file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BacktestMetricFormulaRegistryError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BacktestMetricFormulaRegistryError(
            "backtest_metric_formula_registry YAML must be a mapping"
        )
    raw = payload.get("backtest_metric_formula_registry")
    if not isinstance(raw, dict):
        raise BacktestMetricFormulaRegistryError(
            "backtest_metric_formula_registry YAML must contain a mapping"
        )
    registry = _registry_from_mapping({str(key): value for key, value in raw.items()})
    validate_backtest_metric_formula_registry(registry)
    return registry


def validate_backtest_metric_formula_registry(registry: BacktestMetricFormulaRegistry) -> None:
    """Validate parsed backtest metric formula registry."""

    if not isinstance(registry.version, int):
        raise BacktestMetricFormulaRegistryError("version must exist and be an integer")
    if not registry.status:
        raise BacktestMetricFormulaRegistryError("status must be non-empty")
    if not registry.source_contracts:
        raise BacktestMetricFormulaRegistryError("source_contracts must exist")
    if not registry.registry_scope:
        raise BacktestMetricFormulaRegistryError("registry_scope must exist")
    if not registry.required_series_inputs:
        raise BacktestMetricFormulaRegistryError("required_series_inputs must exist")
    if not registry.metric_definitions:
        raise BacktestMetricFormulaRegistryError("metric_definitions must exist")
    if not registry.prohibited_metric_outputs_now:
        raise BacktestMetricFormulaRegistryError("prohibited_metric_outputs_now must exist")
    if not registry.prohibited_result_fields:
        raise BacktestMetricFormulaRegistryError("prohibited_result_fields must exist")
    if not registry.required_metric_caveats_zh:
        raise BacktestMetricFormulaRegistryError("required_metric_caveats_zh must exist")
    if str(registry.phase_9a2_closure.get("status") or "") != "formula_registry_design_only":
        raise BacktestMetricFormulaRegistryError(
            "phase_9a2_closure.status must be formula_registry_design_only"
        )
    if str(registry.recommended_next_phase.get("phase_id") or "") != "9A3":
        raise BacktestMetricFormulaRegistryError("recommended_next_phase.phase_id must be 9A3")
    _validate_scope(registry.registry_scope)
    _validate_metric_definitions(registry.metric_definitions)
    _validate_prohibited_metric_outputs(
        registry.prohibited_metric_outputs_now,
        registry.metric_definitions,
    )
    _validate_prohibited_result_fields(registry.prohibited_result_fields)
    _validate_required_caveats(registry.required_metric_caveats_zh)
    _validate_caveats(registry.caveats_zh)


def summarize_backtest_metric_formula_registry(
    registry: BacktestMetricFormulaRegistry,
) -> dict[str, Any]:
    """Return a concise machine-readable metric formula registry summary."""

    validate_backtest_metric_formula_registry(registry)
    disallowed = registry.registry_scope["disallowed_now"]
    next_phase = registry.recommended_next_phase
    return {
        "version": registry.version,
        "status": registry.status,
        "metric_count": len(registry.metric_definitions),
        "prohibited_metric_output_count": len(registry.prohibited_metric_outputs_now),
        "prohibited_result_field_count": len(registry.prohibited_result_fields),
        "compute_metric_values_allowed": not bool(disallowed["compute_metric_values"]),
        "execute_backtest_allowed": not bool(disallowed["execute_backtest"]),
        "produce_backtest_results_allowed": not bool(disallowed["produce_backtest_results"]),
        "write_data_backtests_output_allowed": not bool(
            disallowed["write_data_backtests_output"]
        ),
        "write_public_output_allowed": not bool(disallowed["write_public_output"]),
        "produce_allocation_allowed": not bool(disallowed["produce_allocation"]),
        "produce_trade_signal_allowed": not bool(disallowed["produce_trade_signal"]),
        "all_metric_compute_allowed_now": all(
            bool(metric["compute_allowed_now"])
            for metric in registry.metric_definitions.values()
        ),
        "phase_9a2_closure_status": registry.phase_9a2_closure["status"],
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _registry_from_mapping(payload: dict[str, Any]) -> BacktestMetricFormulaRegistry:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "source_contracts",
        "registry_scope",
        "required_series_inputs",
        "metric_definitions",
        "prohibited_metric_outputs_now",
        "prohibited_result_fields",
        "required_metric_caveats_zh",
        "required_acceptance_before_metric_computation",
        "phase_9a2_closure",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise BacktestMetricFormulaRegistryError(
            "backtest_metric_formula_registry missing required field(s): "
            f"{', '.join(missing)}"
        )
    return BacktestMetricFormulaRegistry(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        source_contracts=_mapping_of_mappings(payload["source_contracts"], "source_contracts"),
        registry_scope=_mapping_of_mappings(payload["registry_scope"], "registry_scope"),
        required_series_inputs=_mapping_of_mappings(
            payload["required_series_inputs"],
            "required_series_inputs",
        ),
        metric_definitions=_mapping_of_mappings(
            payload["metric_definitions"],
            "metric_definitions",
        ),
        prohibited_metric_outputs_now=_str_list(
            payload["prohibited_metric_outputs_now"],
            "prohibited_metric_outputs_now",
        ),
        prohibited_result_fields=_str_list(
            payload["prohibited_result_fields"],
            "prohibited_result_fields",
        ),
        required_metric_caveats_zh=_str_list(
            payload["required_metric_caveats_zh"],
            "required_metric_caveats_zh",
        ),
        required_acceptance_before_metric_computation=_list_of_mappings(
            payload["required_acceptance_before_metric_computation"],
            "required_acceptance_before_metric_computation",
        ),
        phase_9a2_closure=_mapping(payload["phase_9a2_closure"], "phase_9a2_closure"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_scope(scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(scope.get("disallowed_now"), "registry_scope.disallowed_now")
    for field in (
        "compute_metric_values",
        "execute_backtest",
        "produce_backtest_results",
        "write_data_backtests_output",
        "write_public_output",
        "produce_allocation",
        "produce_trade_signal",
    ):
        if disallowed.get(field) is not True:
            raise BacktestMetricFormulaRegistryError(
                f"registry_scope.disallowed_now.{field} must be true"
            )


def _validate_metric_definitions(metrics: dict[str, dict[str, Any]]) -> None:
    missing_metrics = sorted(REQUIRED_METRIC_IDS - set(metrics))
    if missing_metrics:
        raise BacktestMetricFormulaRegistryError(
            f"metric_definitions missing metric(s): {', '.join(missing_metrics)}"
        )
    required_fields = {
        "category",
        "formula_text",
        "required_inputs",
        "output_unit",
        "higher_is_better",
        "allowed_in_future_results",
        "compute_allowed_now",
    }
    for metric_id, metric in metrics.items():
        missing_fields = sorted(required_fields - set(metric))
        if missing_fields:
            raise BacktestMetricFormulaRegistryError(
                f"metric_definitions.{metric_id} missing field(s): "
                f"{', '.join(missing_fields)}"
            )
        _str_list(metric["required_inputs"], f"metric_definitions.{metric_id}.required_inputs")
        if metric["compute_allowed_now"] is not False:
            raise BacktestMetricFormulaRegistryError(
                f"metric_definitions.{metric_id}.compute_allowed_now must be false"
            )


def _validate_prohibited_metric_outputs(
    prohibited_outputs: list[str],
    metrics: dict[str, dict[str, Any]],
) -> None:
    missing = sorted(set(metrics) - set(prohibited_outputs))
    if missing:
        raise BacktestMetricFormulaRegistryError(
            f"prohibited_metric_outputs_now missing metric(s): {', '.join(missing)}"
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
        raise BacktestMetricFormulaRegistryError(
            f"prohibited_result_fields missing field(s): {', '.join(missing)}"
        )


def _validate_required_caveats(caveats: list[str]) -> None:
    required = {
        "metric formula registry，不是回測結果。",
        "本階段不計算任何實際績效值。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }
    missing = sorted(required - set(caveats))
    if missing:
        raise BacktestMetricFormulaRegistryError(
            f"required_metric_caveats_zh missing caveat(s): {', '.join(missing)}"
        )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise BacktestMetricFormulaRegistryError("caveats_zh must include 不構成投資建議")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BacktestMetricFormulaRegistryError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise BacktestMetricFormulaRegistryError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BacktestMetricFormulaRegistryError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise BacktestMetricFormulaRegistryError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BacktestMetricFormulaRegistryError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise BacktestMetricFormulaRegistryError(f"{field} must not contain empty items")
    return result
