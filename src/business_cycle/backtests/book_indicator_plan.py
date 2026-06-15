"""Load and validate book-aligned indicator implementation plans."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

VALID_PRIORITIES = {"high", "medium", "low"}
VALID_STATUSES = {"missing", "partial", "existing_needs_refinement"}


class BookAlignedIndicatorImplementationPlanError(ValueError):
    """Raised when a book-aligned indicator implementation plan is invalid."""


@dataclass(frozen=True)
class BookAlignedIndicatorImplementationPlan:
    """Machine-readable implementation plan for book-aligned indicators."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    input_diagnostics: list[dict[str, Any]]
    implementation_batches: list[dict[str, Any]]
    candidate_indicators: list[dict[str, Any]]
    scoring_design_notes: list[dict[str, Any]]
    acceptance_plan: list[dict[str, Any]]
    next_phases: list[dict[str, Any]]


def load_book_aligned_indicator_implementation_plan(
    path: str | Path,
) -> BookAlignedIndicatorImplementationPlan:
    """Load and validate a book-aligned indicator implementation plan YAML."""

    payload = _load_yaml_mapping(path)
    plan = payload.get("book_aligned_indicator_implementation_plan")
    if not isinstance(plan, dict):
        raise BookAlignedIndicatorImplementationPlanError(
            "book_aligned_indicator_implementation_plan YAML must contain a "
            "book_aligned_indicator_implementation_plan mapping"
        )
    parsed = _plan_from_mapping(plan)
    validate_book_aligned_indicator_implementation_plan(parsed)
    return parsed


def validate_book_aligned_indicator_implementation_plan(
    plan: BookAlignedIndicatorImplementationPlan,
) -> None:
    """Validate a parsed book-aligned indicator implementation plan."""

    if not isinstance(plan.version, int):
        raise BookAlignedIndicatorImplementationPlanError("version must exist and be an integer")
    if not plan.status:
        raise BookAlignedIndicatorImplementationPlanError("status must be non-empty")
    if not any("修訂後歷史資料" in caveat for caveat in plan.caveats_zh):
        raise BookAlignedIndicatorImplementationPlanError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in plan.caveats_zh):
        raise BookAlignedIndicatorImplementationPlanError(
            "caveats_zh must include no-investment-advice caveat"
        )
    if not plan.implementation_batches:
        raise BookAlignedIndicatorImplementationPlanError("implementation_batches must exist")
    if not plan.candidate_indicators:
        raise BookAlignedIndicatorImplementationPlanError("candidate_indicators must exist")
    _validate_batches(plan.implementation_batches)
    _validate_candidate_indicators(plan.candidate_indicators)
    _validate_acceptance_plan(plan.acceptance_plan)
    _validate_next_phases(plan.next_phases)


def high_priority_indicator_count(plan: BookAlignedIndicatorImplementationPlan) -> int:
    """Count high-priority candidate indicators."""

    return sum(1 for item in plan.candidate_indicators if item.get("implementation_priority") == "high")


def purpose_groups(plan: BookAlignedIndicatorImplementationPlan) -> list[str]:
    """Return sorted candidate indicator purpose groups."""

    return sorted({str(item["purpose_group"]) for item in plan.candidate_indicators})


def _plan_from_mapping(payload: dict[str, Any]) -> BookAlignedIndicatorImplementationPlan:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "input_diagnostics",
        "implementation_batches",
        "candidate_indicators",
        "scoring_design_notes",
        "acceptance_plan",
        "next_phases",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise BookAlignedIndicatorImplementationPlanError(
            "book_aligned_indicator_implementation_plan missing required field(s): "
            f"{', '.join(missing)}"
        )
    return BookAlignedIndicatorImplementationPlan(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_non_empty_str_list(payload["caveats_zh"], "caveats_zh"),
        input_diagnostics=_list_of_mappings(payload["input_diagnostics"], "input_diagnostics"),
        implementation_batches=_list_of_mappings(
            payload["implementation_batches"],
            "implementation_batches",
        ),
        candidate_indicators=_list_of_mappings(
            payload["candidate_indicators"],
            "candidate_indicators",
        ),
        scoring_design_notes=_list_of_mappings(
            payload["scoring_design_notes"],
            "scoring_design_notes",
        ),
        acceptance_plan=_list_of_mappings(payload["acceptance_plan"], "acceptance_plan"),
        next_phases=_list_of_mappings(payload["next_phases"], "next_phases"),
    )


def _validate_batches(batches: list[dict[str, Any]]) -> None:
    _require_unique_ids(batches, "batch_id", "implementation_batches")
    for batch in batches:
        batch_id = str(batch.get("batch_id") or "")
        _require_text(batch, "display_name_zh", f"batch {batch_id}")
        _require_text(batch, "purpose_zh", f"batch {batch_id}")
        priority = str(batch.get("implementation_priority") or "")
        if priority not in VALID_PRIORITIES:
            raise BookAlignedIndicatorImplementationPlanError(
                f"batch {batch_id} implementation_priority must be high/medium/low"
            )
        _non_empty_str_list(batch.get("validation_scenarios"), f"batch {batch_id}.validation_scenarios")


def _validate_candidate_indicators(items: list[dict[str, Any]]) -> None:
    _require_unique_ids(items, "indicator_id", "candidate_indicators")
    for item in items:
        indicator_id = str(item.get("indicator_id") or "")
        _require_text(item, "display_name_zh", f"candidate {indicator_id}")
        _require_text(item, "purpose_group", f"candidate {indicator_id}")
        status = str(item.get("current_status") or "")
        if status not in VALID_STATUSES:
            raise BookAlignedIndicatorImplementationPlanError(
                f"candidate {indicator_id} current_status must be missing/partial/existing_needs_refinement"
            )
        priority = str(item.get("implementation_priority") or "")
        if priority not in VALID_PRIORITIES:
            raise BookAlignedIndicatorImplementationPlanError(
                f"candidate {indicator_id} implementation_priority must be high/medium/low"
            )
        _require_text(item, "source_priority", f"candidate {indicator_id}")
        _require_text(item, "transformation", f"candidate {indicator_id}")
        _require_text(item, "proposed_score_method", f"candidate {indicator_id}")
        _require_text(item, "expected_phase_impact", f"candidate {indicator_id}")
        if "stale_after_days" not in item or int(item["stale_after_days"]) <= 0:
            raise BookAlignedIndicatorImplementationPlanError(
                f"candidate {indicator_id} stale_after_days must be positive"
            )
        _non_empty_str_list(item.get("validation_scenarios"), f"candidate {indicator_id}.validation_scenarios")


def _validate_acceptance_plan(items: list[dict[str, Any]]) -> None:
    _require_unique_ids(items, "criterion_id", "acceptance_plan")
    for item in items:
        _require_text(item, "description_zh", "acceptance_plan")
        _require_text(item, "target", "acceptance_plan")


def _validate_next_phases(items: list[dict[str, Any]]) -> None:
    _require_unique_ids(items, "phase_id", "next_phases")
    for item in items:
        _require_text(item, "title", "next_phases")


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BookAlignedIndicatorImplementationPlanError(
            f"Book-aligned indicator implementation plan file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BookAlignedIndicatorImplementationPlanError(
            f"Invalid YAML in book-aligned indicator implementation plan file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise BookAlignedIndicatorImplementationPlanError(
            "Book-aligned indicator implementation plan YAML must be a mapping"
        )
    return payload


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BookAlignedIndicatorImplementationPlanError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise BookAlignedIndicatorImplementationPlanError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BookAlignedIndicatorImplementationPlanError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise BookAlignedIndicatorImplementationPlanError(f"{field} entries must be non-empty")
    return items


def _require_unique_ids(items: list[dict[str, Any]], id_field: str, field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id:
            raise BookAlignedIndicatorImplementationPlanError(f"{field} entries must include {id_field}")
        if item_id in seen:
            raise BookAlignedIndicatorImplementationPlanError(
                f"{field} contains duplicate {id_field}: {item_id}"
            )
        seen.add(item_id)


def _require_text(item: dict[str, Any], field: str, context: str) -> None:
    if not str(item.get(field) or ""):
        raise BookAlignedIndicatorImplementationPlanError(
            f"{context} entries must include non-empty {field}"
        )
