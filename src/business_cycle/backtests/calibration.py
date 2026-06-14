"""Load and validate backtest calibration plan specs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class CalibrationPlanError(ValueError):
    """Raised when a calibration plan spec is invalid."""


@dataclass(frozen=True)
class CalibrationPlan:
    """Machine-readable model calibration plan."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    diagnosed_issues: list[dict[str, Any]]
    candidate_model_controls: dict[str, Any]
    calibration_scenarios: dict[str, list[str]]
    acceptance_criteria: list[dict[str, Any]]
    next_phases: list[dict[str, Any]]


def load_calibration_plan(path: str | Path) -> CalibrationPlan:
    """Load and validate a calibration plan YAML file."""

    payload = _load_yaml_mapping(path)
    plan = payload.get("calibration_plan")
    if not isinstance(plan, dict):
        raise CalibrationPlanError("calibration_plan YAML must contain a calibration_plan mapping")
    calibration_plan = _plan_from_mapping(plan)
    validate_calibration_plan(calibration_plan)
    return calibration_plan


def validate_calibration_plan(plan: CalibrationPlan) -> None:
    """Validate a parsed calibration plan."""

    if not isinstance(plan.version, int):
        raise CalibrationPlanError("version must exist and be an integer")
    if not plan.status:
        raise CalibrationPlanError("status must be non-empty")
    if not plan.objective_zh:
        raise CalibrationPlanError("objective_zh must be non-empty")
    if not any("修訂後歷史資料" in caveat for caveat in plan.caveats_zh):
        raise CalibrationPlanError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in plan.caveats_zh):
        raise CalibrationPlanError("caveats_zh must include no-investment-advice caveat")
    if not plan.candidate_model_controls:
        raise CalibrationPlanError("candidate_model_controls must exist")
    _require_unique_ids(plan.diagnosed_issues, "issue_id", "diagnosed_issues")
    _calibration_scenarios(plan.calibration_scenarios)
    _require_unique_ids(plan.acceptance_criteria, "criterion_id", "acceptance_criteria")
    if not plan.next_phases:
        raise CalibrationPlanError("next_phases must exist")
    _require_unique_ids(plan.next_phases, "phase_id", "next_phases")


def _plan_from_mapping(plan: dict[str, Any]) -> CalibrationPlan:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "diagnosed_issues",
        "candidate_model_controls",
        "calibration_scenarios",
        "acceptance_criteria",
        "next_phases",
    )
    missing = [field for field in required if field not in plan]
    if missing:
        raise CalibrationPlanError(f"calibration_plan missing required field(s): {', '.join(missing)}")
    caveats = _non_empty_str_list(plan["caveats_zh"], "caveats_zh")
    if not any("修訂後歷史資料" in caveat for caveat in caveats):
        raise CalibrationPlanError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise CalibrationPlanError("caveats_zh must include no-investment-advice caveat")

    issues = _list_of_mappings(plan["diagnosed_issues"], "diagnosed_issues")
    _require_unique_ids(issues, "issue_id", "diagnosed_issues")
    for issue in issues:
        _require_text(issue, "issue_id", "diagnosed_issues")
        _require_text(issue, "display_name_zh", "diagnosed_issues")
        _require_text(issue, "evidence_zh", "diagnosed_issues")
        _non_empty_str_list(issue.get("likely_causes_zh"), f"diagnosed_issues.{issue['issue_id']}.likely_causes_zh")
        _non_empty_str_list(issue.get("proposed_actions"), f"diagnosed_issues.{issue['issue_id']}.proposed_actions")

    controls = plan["candidate_model_controls"]
    if not isinstance(controls, dict) or not controls:
        raise CalibrationPlanError("candidate_model_controls must be a non-empty mapping")

    scenarios = _calibration_scenarios(plan["calibration_scenarios"])
    criteria = _list_of_mappings(plan["acceptance_criteria"], "acceptance_criteria")
    _require_unique_ids(criteria, "criterion_id", "acceptance_criteria")
    for criterion in criteria:
        _require_text(criterion, "criterion_id", "acceptance_criteria")
        _require_text(criterion, "description_zh", "acceptance_criteria")
        _require_text(criterion, "target", "acceptance_criteria")

    next_phases = _list_of_mappings(plan["next_phases"], "next_phases")
    _require_unique_ids(next_phases, "phase_id", "next_phases")
    for phase in next_phases:
        _require_text(phase, "phase_id", "next_phases")
        _require_text(phase, "title", "next_phases")

    return CalibrationPlan(
        version=int(plan["version"]),
        status=str(plan["status"]),
        objective_zh=str(plan["objective_zh"]),
        caveats_zh=caveats,
        diagnosed_issues=issues,
        candidate_model_controls=controls,
        calibration_scenarios=scenarios,
        acceptance_criteria=criteria,
        next_phases=next_phases,
    )


def _calibration_scenarios(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        raise CalibrationPlanError("calibration_scenarios must be a mapping")
    in_sample = _non_empty_str_list(value.get("in_sample"), "calibration_scenarios.in_sample")
    out_of_sample = _non_empty_str_list(value.get("out_of_sample"), "calibration_scenarios.out_of_sample")
    overlap = sorted(set(in_sample) & set(out_of_sample))
    if overlap:
        raise CalibrationPlanError(f"calibration_scenarios groups must not overlap: {', '.join(overlap)}")
    return {"in_sample": in_sample, "out_of_sample": out_of_sample}


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise CalibrationPlanError(f"Calibration plan file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CalibrationPlanError(f"Invalid YAML in calibration plan file {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CalibrationPlanError("Calibration plan YAML must be a mapping")
    return payload


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise CalibrationPlanError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise CalibrationPlanError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise CalibrationPlanError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise CalibrationPlanError(f"{field} entries must be non-empty")
    return items


def _require_unique_ids(items: list[dict[str, Any]], id_field: str, field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id:
            raise CalibrationPlanError(f"{field} entries must include {id_field}")
        if item_id in seen:
            raise CalibrationPlanError(f"{field} contains duplicate {id_field}: {item_id}")
        seen.add(item_id)


def _require_text(item: dict[str, Any], field: str, context: str) -> None:
    if not str(item.get(field) or ""):
        raise CalibrationPlanError(f"{context} entries must include non-empty {field}")
