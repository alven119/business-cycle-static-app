"""Load and validate portfolio research safety closure checklists."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class PortfolioResearchSafetyClosureError(ValueError):
    """Raised when portfolio research safety closure validation fails."""


@dataclass(frozen=True)
class PortfolioResearchSafetyClosure:
    """Machine-readable Phase 8 portfolio research safety closure checklist."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    artifact_readiness: dict[str, dict[str, Any]]
    validator_readiness: dict[str, dict[str, Any]]
    safety_boundaries: dict[str, Any]
    active_blockers_before_real_backtest: list[dict[str, Any]]
    required_before_real_backtest_prototype: list[dict[str, Any]]
    allowed_future_work: list[dict[str, Any]]
    phase_8_closure: dict[str, Any]
    recommended_next_phase: dict[str, Any]


def load_portfolio_research_safety_closure(
    path: str | Path,
) -> PortfolioResearchSafetyClosure:
    """Load and validate portfolio research safety closure YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise PortfolioResearchSafetyClosureError(
            f"portfolio_research_safety_closure file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PortfolioResearchSafetyClosureError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PortfolioResearchSafetyClosureError(
            "portfolio_research_safety_closure YAML must be a mapping"
        )
    raw = payload.get("portfolio_research_safety_closure")
    if not isinstance(raw, dict):
        raise PortfolioResearchSafetyClosureError(
            "portfolio_research_safety_closure YAML must contain a mapping"
        )
    closure = _closure_from_mapping({str(key): value for key, value in raw.items()})
    validate_portfolio_research_safety_closure(closure)
    return closure


def validate_portfolio_research_safety_closure(
    closure: PortfolioResearchSafetyClosure,
) -> None:
    """Validate parsed portfolio research safety closure checklist."""

    if not isinstance(closure.version, int):
        raise PortfolioResearchSafetyClosureError("version must exist and be an integer")
    if not closure.status:
        raise PortfolioResearchSafetyClosureError("status must be non-empty")
    if not closure.artifact_readiness:
        raise PortfolioResearchSafetyClosureError("artifact_readiness must exist")
    if not closure.validator_readiness:
        raise PortfolioResearchSafetyClosureError("validator_readiness must exist")
    if not closure.safety_boundaries:
        raise PortfolioResearchSafetyClosureError("safety_boundaries must exist")
    if not closure.active_blockers_before_real_backtest:
        raise PortfolioResearchSafetyClosureError(
            "active_blockers_before_real_backtest must exist"
        )
    if not closure.required_before_real_backtest_prototype:
        raise PortfolioResearchSafetyClosureError(
            "required_before_real_backtest_prototype must exist"
        )
    if str(closure.phase_8_closure.get("status") or "") != "ready_to_close_research_only":
        raise PortfolioResearchSafetyClosureError(
            "phase_8_closure.status must be ready_to_close_research_only"
        )
    if str(closure.recommended_next_phase.get("phase_id") or "") != "8I":
        raise PortfolioResearchSafetyClosureError("recommended_next_phase.phase_id must be 8I")
    _validate_safety_boundaries(closure.safety_boundaries)
    _validate_active_blockers(closure.active_blockers_before_real_backtest)
    _validate_required_targets(closure.required_before_real_backtest_prototype)
    _validate_caveats(closure.caveats_zh)


def summarize_portfolio_research_safety_closure(
    closure: PortfolioResearchSafetyClosure,
) -> dict[str, Any]:
    """Return a concise machine-readable closure summary."""

    validate_portfolio_research_safety_closure(closure)
    boundaries = closure.safety_boundaries
    next_phase = closure.recommended_next_phase
    return {
        "version": closure.version,
        "status": closure.status,
        "artifact_count": len(closure.artifact_readiness),
        "validator_count": len(closure.validator_readiness),
        "active_blocker_count": sum(
            1 for blocker in closure.active_blockers_before_real_backtest if blocker.get("active") is True
        ),
        "required_before_real_backtest_count": len(
            closure.required_before_real_backtest_prototype
        ),
        "phase_8_closure_status": closure.phase_8_closure["status"],
        "research_only": bool(boundaries["research_only"]),
        "structural_dry_run_only": bool(boundaries["structural_dry_run_only"]),
        "formal_backtest_executed": bool(boundaries["formal_backtest_executed"]),
        "performance_metrics_computed": bool(boundaries["performance_metrics_computed"]),
        "allocation_output_generated": bool(boundaries["allocation_output_generated"]),
        "trade_signal_generated": bool(boundaries["trade_signal_generated"]),
        "data_backtests_output_written": bool(boundaries["data_backtests_output_written"]),
        "public_output_written": bool(boundaries["public_output_written"]),
        "live_recommendation_allowed": bool(boundaries["live_recommendation_allowed"]),
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _closure_from_mapping(payload: dict[str, Any]) -> PortfolioResearchSafetyClosure:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "artifact_readiness",
        "validator_readiness",
        "safety_boundaries",
        "active_blockers_before_real_backtest",
        "required_before_real_backtest_prototype",
        "allowed_future_work",
        "phase_8_closure",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise PortfolioResearchSafetyClosureError(
            "portfolio_research_safety_closure missing required field(s): "
            f"{', '.join(missing)}"
        )
    return PortfolioResearchSafetyClosure(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        artifact_readiness=_mapping_of_mappings(
            payload["artifact_readiness"],
            "artifact_readiness",
        ),
        validator_readiness=_mapping_of_mappings(
            payload["validator_readiness"],
            "validator_readiness",
        ),
        safety_boundaries=_mapping(payload["safety_boundaries"], "safety_boundaries"),
        active_blockers_before_real_backtest=_list_of_mappings(
            payload["active_blockers_before_real_backtest"],
            "active_blockers_before_real_backtest",
        ),
        required_before_real_backtest_prototype=_list_of_mappings(
            payload["required_before_real_backtest_prototype"],
            "required_before_real_backtest_prototype",
        ),
        allowed_future_work=_list_of_mappings(payload["allowed_future_work"], "allowed_future_work"),
        phase_8_closure=_mapping(payload["phase_8_closure"], "phase_8_closure"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_safety_boundaries(boundaries: dict[str, Any]) -> None:
    expected = {
        "research_only": True,
        "structural_dry_run_only": True,
        "formal_backtest_executed": False,
        "performance_metrics_computed": False,
        "allocation_output_generated": False,
        "trade_signal_generated": False,
        "data_backtests_output_written": False,
        "public_output_written": False,
        "live_recommendation_allowed": False,
    }
    for field, expected_value in expected.items():
        if boundaries.get(field) is not expected_value:
            raise PortfolioResearchSafetyClosureError(
                f"safety_boundaries.{field} must be {str(expected_value).lower()}"
            )


def _validate_active_blockers(blockers: list[dict[str, Any]]) -> None:
    if not any(blocker.get("active") is True for blocker in blockers):
        raise PortfolioResearchSafetyClosureError(
            "active_blockers_before_real_backtest must include at least one active blocker"
        )


def _validate_required_targets(targets: list[dict[str, Any]]) -> None:
    target_ids = {str(target.get("target_id") or "") for target in targets}
    required = {
        "real_backtest_engine_contract_defined",
        "result_output_contract_defined",
        "metric_formula_registry_defined",
        "no_live_allocation_result_validator_defined",
        "backtest_result_caveat_required",
        "output_location_policy_defined",
    }
    missing = sorted(required - target_ids)
    if missing:
        raise PortfolioResearchSafetyClosureError(
            "required_before_real_backtest_prototype missing target(s): "
            f"{', '.join(missing)}"
        )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise PortfolioResearchSafetyClosureError("caveats_zh must include 不構成投資建議")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PortfolioResearchSafetyClosureError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise PortfolioResearchSafetyClosureError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise PortfolioResearchSafetyClosureError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise PortfolioResearchSafetyClosureError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PortfolioResearchSafetyClosureError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise PortfolioResearchSafetyClosureError(f"{field} must not contain empty items")
    return result
