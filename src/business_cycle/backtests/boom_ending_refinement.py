"""Load and validate boom-ending refinement plans."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class BoomEndingRefinementPlanError(ValueError):
    """Raised when a boom-ending refinement plan is invalid."""


@dataclass(frozen=True)
class BoomEndingRefinementPlan:
    """Machine-readable boom-ending scoring refinement plan."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    input_findings: dict[str, Any]
    diagnosed_issues: list[dict[str, Any]]
    proposed_refinements: list[dict[str, Any]]
    recommended_next_phase: dict[str, Any]


def load_boom_ending_refinement_plan(path: str | Path) -> BoomEndingRefinementPlan:
    """Load and validate a boom-ending refinement plan YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("boom_ending_refinement_plan")
    if not isinstance(raw, dict):
        raise BoomEndingRefinementPlanError(
            "boom_ending_refinement_plan YAML must contain a boom_ending_refinement_plan mapping"
        )
    plan = BoomEndingRefinementPlan(
        version=int(raw.get("version", 0)),
        status=str(raw.get("status", "")),
        data_mode=str(raw.get("data_mode", "")),
        objective_zh=str(raw.get("objective_zh", "")),
        caveats_zh=_non_empty_str_list(raw.get("caveats_zh"), "caveats_zh"),
        input_findings=_mapping(raw.get("input_findings"), "input_findings"),
        diagnosed_issues=_list_of_mappings(raw.get("diagnosed_issues"), "diagnosed_issues"),
        proposed_refinements=_list_of_mappings(raw.get("proposed_refinements"), "proposed_refinements"),
        recommended_next_phase=_mapping(raw.get("recommended_next_phase"), "recommended_next_phase"),
    )
    validate_boom_ending_refinement_plan(plan)
    return plan


def validate_boom_ending_refinement_plan(plan: BoomEndingRefinementPlan) -> None:
    """Validate a parsed boom-ending refinement plan."""

    if not isinstance(plan.version, int) or plan.version < 1:
        raise BoomEndingRefinementPlanError("version must exist and be a positive integer")
    if not plan.status:
        raise BoomEndingRefinementPlanError("status must exist")
    if not plan.diagnosed_issues:
        raise BoomEndingRefinementPlanError("diagnosed_issues must exist")
    if not plan.proposed_refinements:
        raise BoomEndingRefinementPlanError("proposed_refinements must exist")
    if plan.recommended_next_phase.get("phase_id") != "7F2.3":
        raise BoomEndingRefinementPlanError("recommended_next_phase.phase_id must be 7F2.3")
    if not any("修訂後歷史資料" in caveat for caveat in plan.caveats_zh):
        raise BoomEndingRefinementPlanError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in plan.caveats_zh):
        raise BoomEndingRefinementPlanError("caveats_zh must include no-investment-advice caveat")
    _require_unique_ids(plan.diagnosed_issues, "issue_id", "diagnosed_issues")
    _require_unique_ids(plan.proposed_refinements, "refinement_id", "proposed_refinements")


def high_priority_refinement_count(plan: BoomEndingRefinementPlan) -> int:
    """Count high-priority refinements."""

    return sum(1 for item in plan.proposed_refinements if item.get("priority") == "high")


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BoomEndingRefinementPlanError(f"Boom ending refinement plan file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BoomEndingRefinementPlanError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BoomEndingRefinementPlanError("Boom ending refinement plan YAML must be a mapping")
    return payload


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise BoomEndingRefinementPlanError(f"{field} must be a non-empty mapping")
    return value


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BoomEndingRefinementPlanError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise BoomEndingRefinementPlanError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BoomEndingRefinementPlanError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise BoomEndingRefinementPlanError(f"{field} entries must be non-empty")
    return items


def _require_unique_ids(items: list[dict[str, Any]], id_field: str, field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id:
            raise BoomEndingRefinementPlanError(f"{field} entries must include {id_field}")
        if item_id in seen:
            raise BoomEndingRefinementPlanError(f"{field} contains duplicate {id_field}: {item_id}")
        seen.add(item_id)
