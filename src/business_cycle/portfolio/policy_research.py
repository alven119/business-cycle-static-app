"""Load and validate portfolio policy research planning specs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class PortfolioPolicyResearchPlanError(ValueError):
    """Raised when portfolio policy research plan is invalid."""


@dataclass(frozen=True)
class PortfolioPolicyResearchPlan:
    """Machine-readable portfolio policy research plan."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    policy_scope: dict[str, Any]
    evidence_inputs: dict[str, dict[str, Any]]
    research_policy_templates: dict[str, dict[str, Any]]
    required_backtest_dimensions: dict[str, list[str]]
    required_acceptance_before_policy_backtest: list[dict[str, Any]]
    recommended_next_phase: dict[str, Any]


def load_portfolio_policy_research_plan(path: str | Path) -> PortfolioPolicyResearchPlan:
    """Load and validate portfolio policy research plan YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise PortfolioPolicyResearchPlanError(
            f"Portfolio policy research plan file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PortfolioPolicyResearchPlanError(
            f"Invalid YAML in portfolio policy research plan file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise PortfolioPolicyResearchPlanError("Portfolio policy research plan YAML must be a mapping")
    raw = payload.get("portfolio_policy_research_plan")
    if not isinstance(raw, dict):
        raise PortfolioPolicyResearchPlanError(
            "portfolio_policy_research_plan YAML must contain a mapping"
        )
    plan = _plan_from_mapping(raw)
    validate_portfolio_policy_research_plan(plan)
    return plan


def validate_portfolio_policy_research_plan(plan: PortfolioPolicyResearchPlan) -> None:
    """Validate parsed portfolio policy research plan."""

    if not isinstance(plan.version, int):
        raise PortfolioPolicyResearchPlanError("version must exist and be an integer")
    if not plan.status:
        raise PortfolioPolicyResearchPlanError("status must be non-empty")
    _validate_caveats(plan.caveats_zh)
    _validate_policy_scope(plan.policy_scope)
    if not plan.evidence_inputs:
        raise PortfolioPolicyResearchPlanError("evidence_inputs must exist")
    _validate_templates(plan.research_policy_templates)
    _validate_backtest_dimensions(plan.required_backtest_dimensions)
    _validate_required_acceptance(plan.required_acceptance_before_policy_backtest)
    _validate_recommended_next_phase(plan.recommended_next_phase)


def summarize_portfolio_policy_research_plan(plan: PortfolioPolicyResearchPlan) -> dict[str, Any]:
    """Return a concise machine-readable portfolio policy research plan summary."""

    disallowed = _mapping(plan.policy_scope["disallowed_now"], "policy_scope.disallowed_now")
    next_phase = plan.recommended_next_phase
    return {
        "version": plan.version,
        "status": plan.status,
        "template_count": len(plan.research_policy_templates),
        "metric_count": len(plan.required_backtest_dimensions["metrics"]),
        "sensitivity_test_count": len(plan.required_backtest_dimensions["sensitivity_tests"]),
        "live_allocation_allowed_now": not bool(disallowed["live_allocation_output"]),
        "trade_signal_generation_allowed_now": not bool(disallowed["trade_signal_generation"]),
        "public_output_allowed_now": not bool(disallowed["public_output"]),
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _plan_from_mapping(payload: dict[str, Any]) -> PortfolioPolicyResearchPlan:
    required = (
        "version",
        "status",
        "data_mode",
        "objective_zh",
        "caveats_zh",
        "policy_scope",
        "evidence_inputs",
        "research_policy_templates",
        "required_backtest_dimensions",
        "required_acceptance_before_policy_backtest",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise PortfolioPolicyResearchPlanError(
            "portfolio_policy_research_plan missing required field(s): "
            f"{', '.join(missing)}"
        )
    return PortfolioPolicyResearchPlan(
        version=int(payload["version"]),
        status=str(payload["status"]),
        data_mode=str(payload["data_mode"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        policy_scope=_mapping(payload["policy_scope"], "policy_scope"),
        evidence_inputs=_mapping_of_mappings(payload["evidence_inputs"], "evidence_inputs"),
        research_policy_templates=_mapping_of_mappings(
            payload["research_policy_templates"],
            "research_policy_templates",
        ),
        required_backtest_dimensions=_mapping_of_str_lists(
            payload["required_backtest_dimensions"],
            "required_backtest_dimensions",
        ),
        required_acceptance_before_policy_backtest=_list_of_mappings(
            payload["required_acceptance_before_policy_backtest"],
            "required_acceptance_before_policy_backtest",
        ),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_caveats(caveats: list[str]) -> None:
    for required in (
        "不是正式投資策略",
        "future backtest-only parameters",
        "不是目前配置建議",
        "不是買賣訊號",
        "不構成投資建議",
    ):
        if not any(required in caveat for caveat in caveats):
            raise PortfolioPolicyResearchPlanError(f"caveats_zh must include {required}")


def _validate_policy_scope(policy_scope: dict[str, Any]) -> None:
    if "allowed_now" not in policy_scope:
        raise PortfolioPolicyResearchPlanError("policy_scope.allowed_now must exist")
    disallowed = _mapping(policy_scope.get("disallowed_now"), "policy_scope.disallowed_now")
    for field in (
        "live_allocation_output",
        "current_market_recommendation",
        "trade_signal_generation",
        "public_output",
    ):
        if disallowed.get(field) is not True:
            raise PortfolioPolicyResearchPlanError(f"disallowed_now.{field} must be true")


def _validate_templates(templates: dict[str, dict[str, Any]]) -> None:
    required_templates = {
        "boom_de_risking_template",
        "recession_defense_template",
        "recovery_re_risking_template",
    }
    missing = sorted(required_templates - set(templates))
    if missing:
        raise PortfolioPolicyResearchPlanError(
            f"research_policy_templates missing required template(s): {', '.join(missing)}"
        )
    boom = templates["boom_de_risking_template"]
    params = _mapping(boom.get("book_aligned_parameters"), "boom_de_risking_template.book_aligned_parameters")
    weights = [float(value) for value in params.get("stock_weight_levels_for_backtest_only", [])]
    if weights != [0.70, 0.50, 0.30]:
        raise PortfolioPolicyResearchPlanError(
            "boom_de_risking_template must define backtest-only stock weights [0.70, 0.50, 0.30]"
        )
    for template_id in sorted(required_templates):
        template = templates[template_id]
        prohibited = _str_list(
            template.get("prohibited_interpretations_zh"),
            f"{template_id}.prohibited_interpretations_zh",
        )
        if not any(
            ("交易訊號" in item or "配置建議" in item or "買進" in item or "賣出" in item)
            for item in prohibited
        ):
            raise PortfolioPolicyResearchPlanError(
                f"{template_id}.prohibited_interpretations_zh must prohibit direct trade signal or current allocation interpretation"
            )


def _validate_backtest_dimensions(dimensions: dict[str, list[str]]) -> None:
    for field in ("historical_scenarios", "metrics", "sensitivity_tests", "data_limitations"):
        if field not in dimensions:
            raise PortfolioPolicyResearchPlanError(f"required_backtest_dimensions.{field} must exist")
    metrics = set(dimensions["metrics"])
    for metric in ("max_drawdown", "turnover", "false_de_risk_cost", "false_re_risk_cost"):
        if metric not in metrics:
            raise PortfolioPolicyResearchPlanError(
                f"required_backtest_dimensions.metrics must include {metric}"
            )


def _validate_required_acceptance(targets: list[dict[str, Any]]) -> None:
    target_ids = {str(target.get("target_id")) for target in targets}
    for target_id in (
        "no_live_allocation_output",
        "no_trade_signal_language",
        "not_investment_advice_caveat",
    ):
        if target_id not in target_ids:
            raise PortfolioPolicyResearchPlanError(
                f"required_acceptance_before_policy_backtest must include {target_id}"
            )


def _validate_recommended_next_phase(next_phase: dict[str, Any]) -> None:
    if str(next_phase.get("phase_id") or "") != "8B":
        raise PortfolioPolicyResearchPlanError("recommended_next_phase.phase_id must be 8B")
    if not str(next_phase.get("reason_zh") or ""):
        raise PortfolioPolicyResearchPlanError("recommended_next_phase must include reason_zh")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PortfolioPolicyResearchPlanError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise PortfolioPolicyResearchPlanError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _mapping_of_str_lists(value: Any, field: str) -> dict[str, list[str]]:
    mapping = _mapping(value, field)
    return {key: _str_list(raw, f"{field}.{key}") for key, raw in mapping.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise PortfolioPolicyResearchPlanError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise PortfolioPolicyResearchPlanError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PortfolioPolicyResearchPlanError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise PortfolioPolicyResearchPlanError(f"{field} must not contain empty items")
    return result
