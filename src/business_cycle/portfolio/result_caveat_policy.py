"""Load and validate backtest result caveat policies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class BacktestResultCaveatPolicyError(ValueError):
    """Raised when backtest result caveat policy validation fails."""


@dataclass(frozen=True)
class BacktestResultCaveatPolicy:
    """Machine-readable backtest result caveat policy."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    source_contracts: dict[str, dict[str, Any]]
    caveat_policy_scope: dict[str, dict[str, Any]]
    required_global_caveats_zh: list[str]
    required_contextual_caveats_zh: dict[str, dict[str, Any]]
    display_requirements: dict[str, Any]
    prohibited_text_patterns: dict[str, list[str]]
    prohibited_result_interpretations_zh: list[str]
    future_result_validation_rules: list[dict[str, Any]]
    required_acceptance_before_result_generation: list[dict[str, Any]]
    prohibited_result_fields: list[str]
    phase_9a4_closure: dict[str, Any]
    recommended_next_phase: dict[str, Any]


def load_backtest_result_caveat_policy(path: str | Path) -> BacktestResultCaveatPolicy:
    """Load and validate backtest result caveat policy YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BacktestResultCaveatPolicyError(
            f"backtest_result_caveat_policy file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BacktestResultCaveatPolicyError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BacktestResultCaveatPolicyError(
            "backtest_result_caveat_policy YAML must be a mapping"
        )
    raw = payload.get("backtest_result_caveat_policy")
    if not isinstance(raw, dict):
        raise BacktestResultCaveatPolicyError(
            "backtest_result_caveat_policy YAML must contain a mapping"
        )
    policy = _policy_from_mapping({str(key): value for key, value in raw.items()})
    validate_backtest_result_caveat_policy(policy)
    return policy


def validate_backtest_result_caveat_policy(policy: BacktestResultCaveatPolicy) -> None:
    """Validate parsed backtest result caveat policy."""

    if not isinstance(policy.version, int):
        raise BacktestResultCaveatPolicyError("version must exist and be an integer")
    if not policy.status:
        raise BacktestResultCaveatPolicyError("status must be non-empty")
    if not policy.source_contracts:
        raise BacktestResultCaveatPolicyError("source_contracts must exist")
    if not policy.caveat_policy_scope:
        raise BacktestResultCaveatPolicyError("caveat_policy_scope must exist")
    if not policy.required_global_caveats_zh:
        raise BacktestResultCaveatPolicyError("required_global_caveats_zh must exist")
    if not policy.required_contextual_caveats_zh:
        raise BacktestResultCaveatPolicyError("required_contextual_caveats_zh must exist")
    if not policy.display_requirements:
        raise BacktestResultCaveatPolicyError("display_requirements must exist")
    if not policy.prohibited_text_patterns:
        raise BacktestResultCaveatPolicyError("prohibited_text_patterns must exist")
    if not policy.prohibited_result_interpretations_zh:
        raise BacktestResultCaveatPolicyError(
            "prohibited_result_interpretations_zh must exist"
        )
    if not policy.future_result_validation_rules:
        raise BacktestResultCaveatPolicyError("future_result_validation_rules must exist")
    if not policy.required_acceptance_before_result_generation:
        raise BacktestResultCaveatPolicyError(
            "required_acceptance_before_result_generation must exist"
        )
    if not policy.prohibited_result_fields:
        raise BacktestResultCaveatPolicyError("prohibited_result_fields must exist")
    if str(policy.phase_9a4_closure.get("status") or "") != "caveat_policy_design_only":
        raise BacktestResultCaveatPolicyError(
            "phase_9a4_closure.status must be caveat_policy_design_only"
        )
    if str(policy.recommended_next_phase.get("phase_id") or "") != "9A5":
        raise BacktestResultCaveatPolicyError("recommended_next_phase.phase_id must be 9A5")
    _validate_scope(policy.caveat_policy_scope)
    _validate_required_global_caveats(policy.required_global_caveats_zh)
    _validate_required_contextual_caveats(policy.required_contextual_caveats_zh)
    _validate_display_requirements(policy.display_requirements)
    _validate_prohibited_text_patterns(policy.prohibited_text_patterns)
    _validate_required_acceptance(policy.required_acceptance_before_result_generation)
    _validate_prohibited_result_fields(policy.prohibited_result_fields)
    _validate_caveats(policy.caveats_zh)


def summarize_backtest_result_caveat_policy(
    policy: BacktestResultCaveatPolicy,
) -> dict[str, Any]:
    """Return a concise machine-readable result caveat policy summary."""

    validate_backtest_result_caveat_policy(policy)
    disallowed = policy.caveat_policy_scope["disallowed_now"]
    display = policy.display_requirements
    next_phase = policy.recommended_next_phase
    return {
        "version": policy.version,
        "status": policy.status,
        "required_global_caveat_count": len(policy.required_global_caveats_zh),
        "contextual_caveat_count": len(policy.required_contextual_caveats_zh),
        "prohibited_text_pattern_count": sum(
            len(patterns) for patterns in policy.prohibited_text_patterns.values()
        ),
        "prohibited_result_field_count": len(policy.prohibited_result_fields),
        "future_validation_rule_count": len(policy.future_result_validation_rules),
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
        "caveats_visible_before_metrics": bool(
            display["must_be_visible_before_any_metric_value"]
        ),
        "phase_9a4_closure_status": policy.phase_9a4_closure["status"],
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _policy_from_mapping(payload: dict[str, Any]) -> BacktestResultCaveatPolicy:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "source_contracts",
        "caveat_policy_scope",
        "required_global_caveats_zh",
        "required_contextual_caveats_zh",
        "display_requirements",
        "prohibited_text_patterns",
        "prohibited_result_interpretations_zh",
        "future_result_validation_rules",
        "required_acceptance_before_result_generation",
        "prohibited_result_fields",
        "phase_9a4_closure",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise BacktestResultCaveatPolicyError(
            "backtest_result_caveat_policy missing required field(s): "
            f"{', '.join(missing)}"
        )
    return BacktestResultCaveatPolicy(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        source_contracts=_mapping_of_mappings(payload["source_contracts"], "source_contracts"),
        caveat_policy_scope=_mapping_of_mappings(
            payload["caveat_policy_scope"],
            "caveat_policy_scope",
        ),
        required_global_caveats_zh=_str_list(
            payload["required_global_caveats_zh"],
            "required_global_caveats_zh",
        ),
        required_contextual_caveats_zh=_mapping_of_mappings(
            payload["required_contextual_caveats_zh"],
            "required_contextual_caveats_zh",
        ),
        display_requirements=_mapping(
            payload["display_requirements"],
            "display_requirements",
        ),
        prohibited_text_patterns=_mapping_of_str_lists(
            payload["prohibited_text_patterns"],
            "prohibited_text_patterns",
        ),
        prohibited_result_interpretations_zh=_str_list(
            payload["prohibited_result_interpretations_zh"],
            "prohibited_result_interpretations_zh",
        ),
        future_result_validation_rules=_list_of_mappings(
            payload["future_result_validation_rules"],
            "future_result_validation_rules",
        ),
        required_acceptance_before_result_generation=_list_of_mappings(
            payload["required_acceptance_before_result_generation"],
            "required_acceptance_before_result_generation",
        ),
        prohibited_result_fields=_str_list(
            payload["prohibited_result_fields"],
            "prohibited_result_fields",
        ),
        phase_9a4_closure=_mapping(payload["phase_9a4_closure"], "phase_9a4_closure"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_scope(scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(scope.get("disallowed_now"), "caveat_policy_scope.disallowed_now")
    for field in (
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
            raise BacktestResultCaveatPolicyError(
                f"caveat_policy_scope.disallowed_now.{field} must be true"
            )


def _validate_required_global_caveats(caveats: list[str]) -> None:
    required = {
        "backtest-only，不是目前配置建議。",
        "回測結果不代表未來績效。",
        "不構成投資建議。",
    }
    missing = sorted(required - set(caveats))
    if missing:
        raise BacktestResultCaveatPolicyError(
            f"required_global_caveats_zh missing caveat(s): {', '.join(missing)}"
        )


def _validate_required_contextual_caveats(caveats: dict[str, dict[str, Any]]) -> None:
    required = {
        "revised_data",
        "transaction_cost",
        "false_signal_cost",
        "scenario_specific",
        "covid_exogenous_shock",
    }
    missing = sorted(required - set(caveats))
    if missing:
        raise BacktestResultCaveatPolicyError(
            f"required_contextual_caveats_zh missing caveat(s): {', '.join(missing)}"
        )


def _validate_display_requirements(requirements: dict[str, Any]) -> None:
    if requirements.get("must_be_visible_before_any_metric_value") is not True:
        raise BacktestResultCaveatPolicyError(
            "display_requirements.must_be_visible_before_any_metric_value must be true"
        )
    if requirements.get("must_not_be_collapsible_only") is not True:
        raise BacktestResultCaveatPolicyError(
            "display_requirements.must_not_be_collapsible_only must be true"
        )


def _validate_prohibited_text_patterns(patterns_by_language: dict[str, list[str]]) -> None:
    patterns = {pattern for patterns in patterns_by_language.values() for pattern in patterns}
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
        raise BacktestResultCaveatPolicyError(
            f"prohibited_text_patterns missing pattern(s): {', '.join(missing)}"
        )


def _validate_required_acceptance(acceptance: list[dict[str, Any]]) -> None:
    target_ids = {str(item.get("target_id") or "") for item in acceptance}
    required = {
        "caveat_policy_validated",
        "result_output_contract_validated",
        "output_location_policy_validated",
        "result_safety_validator_available",
        "no_prohibited_text_validator_available",
        "no_public_auto_output",
        "no_live_allocation_or_trade_signal",
    }
    missing = sorted(required - target_ids)
    if missing:
        raise BacktestResultCaveatPolicyError(
            "required_acceptance_before_result_generation missing target_id(s): "
            f"{', '.join(missing)}"
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
        raise BacktestResultCaveatPolicyError(
            f"prohibited_result_fields missing field(s): {', '.join(missing)}"
        )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise BacktestResultCaveatPolicyError("caveats_zh must include 不構成投資建議")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BacktestResultCaveatPolicyError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise BacktestResultCaveatPolicyError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _mapping_of_str_lists(value: Any, field: str) -> dict[str, list[str]]:
    mapping = _mapping(value, field)
    return {key: _str_list(raw, f"{field}.{key}") for key, raw in mapping.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BacktestResultCaveatPolicyError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise BacktestResultCaveatPolicyError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BacktestResultCaveatPolicyError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise BacktestResultCaveatPolicyError(f"{field} must not contain empty items")
    return result
