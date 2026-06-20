"""Load and validate recovery refinement plans."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class RecoveryRefinementPlanError(ValueError):
    """Raised when a recovery refinement plan is invalid."""


@dataclass(frozen=True)
class RecoveryRefinementPlan:
    """Machine-readable recovery diagnostics refinement plan."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    input_findings: dict[str, Any]
    diagnosed_issues: list[dict[str, Any]]
    proposed_refinements: list[dict[str, Any]]
    recommended_next_phase: dict[str, Any]


def load_recovery_refinement_plan(path: str | Path) -> RecoveryRefinementPlan:
    """Load and validate a recovery refinement plan YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("recovery_refinement_plan")
    if not isinstance(raw, dict):
        raise RecoveryRefinementPlanError(
            "recovery_refinement_plan YAML must contain a recovery_refinement_plan mapping"
        )
    plan = RecoveryRefinementPlan(
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
    validate_recovery_refinement_plan(plan)
    return plan


def validate_recovery_refinement_plan(plan: RecoveryRefinementPlan) -> None:
    """Validate a parsed recovery refinement plan."""

    if not isinstance(plan.version, int) or plan.version < 1:
        raise RecoveryRefinementPlanError("version must exist and be a positive integer")
    if not plan.status:
        raise RecoveryRefinementPlanError("status must exist")
    if not plan.diagnosed_issues:
        raise RecoveryRefinementPlanError("diagnosed_issues must exist")
    if not plan.proposed_refinements:
        raise RecoveryRefinementPlanError("proposed_refinements must exist")
    if plan.recommended_next_phase.get("phase_id") != "7F3.3":
        raise RecoveryRefinementPlanError("recommended_next_phase.phase_id must be 7F3.3")
    _require_caveat(plan.caveats_zh, "修訂後歷史資料", "revised data")
    _require_caveat(plan.caveats_zh, "recovery watch 不等於正式復甦確認", "recovery watch caveat")
    _require_caveat(plan.caveats_zh, "policy easing 不得單獨確認 recovery", "policy easing caveat")
    _require_caveat(plan.caveats_zh, "不構成投資建議", "no-investment-advice caveat")
    _require_unique_ids(plan.diagnosed_issues, "issue_id", "diagnosed_issues")
    _require_unique_ids(plan.proposed_refinements, "refinement_id", "proposed_refinements")
    refinement_ids = {str(item.get("refinement_id")) for item in plan.proposed_refinements}
    for required in {"recession_context_gate", "policy_and_financial_support_cap"}:
        if required not in refinement_ids:
            raise RecoveryRefinementPlanError(f"proposed_refinements must include {required}")


def high_priority_recovery_refinement_count(plan: RecoveryRefinementPlan) -> int:
    """Count high-priority recovery refinements."""

    return sum(1 for item in plan.proposed_refinements if item.get("priority") == "high")


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise RecoveryRefinementPlanError(f"Recovery refinement plan file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RecoveryRefinementPlanError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RecoveryRefinementPlanError("Recovery refinement plan YAML must be a mapping")
    return payload


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise RecoveryRefinementPlanError(f"{field} must be a non-empty mapping")
    return value


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RecoveryRefinementPlanError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise RecoveryRefinementPlanError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RecoveryRefinementPlanError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise RecoveryRefinementPlanError(f"{field} entries must be non-empty")
    return items


def _require_unique_ids(items: list[dict[str, Any]], id_field: str, field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id:
            raise RecoveryRefinementPlanError(f"{field} entries must include {id_field}")
        if item_id in seen:
            raise RecoveryRefinementPlanError(f"{field} contains duplicate {id_field}: {item_id}")
        seen.add(item_id)


def _require_caveat(caveats: list[str], required_text: str, label: str) -> None:
    if not any(required_text in caveat for caveat in caveats):
        raise RecoveryRefinementPlanError(f"caveats_zh must include {label}")
