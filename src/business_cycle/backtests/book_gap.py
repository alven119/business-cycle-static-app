"""Load and validate book-aligned indicator gap analysis specs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

VALID_COVERAGE_STATUSES = {"covered", "partial", "missing"}
VALID_PRIORITIES = {"high", "medium", "low"}


class BookIndicatorGapAnalysisError(ValueError):
    """Raised when book indicator gap analysis spec is invalid."""


@dataclass(frozen=True)
class BookIndicatorGapAnalysis:
    """Machine-readable book-aligned indicator gap analysis."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    current_mvp_indicator_ids: list[str]
    book_aligned_indicator_groups: list[dict[str, Any]]
    gap_items: list[dict[str, Any]]
    priority_recommendations: list[dict[str, Any]]
    next_phases: list[dict[str, Any]]


def load_book_indicator_gap_analysis(path: str | Path) -> BookIndicatorGapAnalysis:
    """Load and validate book indicator gap analysis YAML."""

    payload = _load_yaml_mapping(path)
    analysis = payload.get("book_indicator_gap_analysis")
    if not isinstance(analysis, dict):
        raise BookIndicatorGapAnalysisError(
            "book_indicator_gap_analysis YAML must contain a book_indicator_gap_analysis mapping"
        )
    parsed = _analysis_from_mapping(analysis)
    validate_book_indicator_gap_analysis(parsed)
    return parsed


def validate_book_indicator_gap_analysis(analysis: BookIndicatorGapAnalysis) -> None:
    """Validate a parsed book indicator gap analysis."""

    if not isinstance(analysis.version, int):
        raise BookIndicatorGapAnalysisError("version must exist and be an integer")
    if not analysis.status:
        raise BookIndicatorGapAnalysisError("status must be non-empty")
    if not any("修訂後歷史資料" in caveat for caveat in analysis.caveats_zh):
        raise BookIndicatorGapAnalysisError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in analysis.caveats_zh):
        raise BookIndicatorGapAnalysisError("caveats_zh must include no-investment-advice caveat")
    if not analysis.book_aligned_indicator_groups:
        raise BookIndicatorGapAnalysisError("book_aligned_indicator_groups must exist")
    if not analysis.gap_items:
        raise BookIndicatorGapAnalysisError("gap_items must exist")
    if not analysis.priority_recommendations:
        raise BookIndicatorGapAnalysisError("priority_recommendations must exist")
    _validate_groups(analysis.book_aligned_indicator_groups)
    _validate_gap_items(analysis.gap_items)
    _validate_recommendations(analysis.priority_recommendations)
    _validate_next_phases(analysis.next_phases)


def sensitivity_issues(analysis: BookIndicatorGapAnalysis) -> list[dict[str, Any]]:
    """Return flattened sensitivity issue entries."""

    issues: list[dict[str, Any]] = []
    for group in analysis.book_aligned_indicator_groups:
        for issue in _list_of_mappings_allow_empty(group.get("sensitivity_issues")):
            issues.append(issue)
    return issues


def high_priority_count(analysis: BookIndicatorGapAnalysis) -> int:
    """Count high-priority groups and recommendations."""

    group_count = sum(
        1
        for group in analysis.book_aligned_indicator_groups
        if group.get("implementation_priority") == "high"
    )
    recommendation_count = sum(
        1
        for item in analysis.priority_recommendations
        if item.get("priority") == "high"
    )
    return group_count + recommendation_count


def _analysis_from_mapping(payload: dict[str, Any]) -> BookIndicatorGapAnalysis:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "current_mvp_indicator_ids",
        "book_aligned_indicator_groups",
        "gap_items",
        "priority_recommendations",
        "next_phases",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise BookIndicatorGapAnalysisError(
            f"book_indicator_gap_analysis missing required field(s): {', '.join(missing)}"
        )
    return BookIndicatorGapAnalysis(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_non_empty_str_list(payload["caveats_zh"], "caveats_zh"),
        current_mvp_indicator_ids=_non_empty_str_list(
            payload["current_mvp_indicator_ids"],
            "current_mvp_indicator_ids",
        ),
        book_aligned_indicator_groups=_list_of_mappings(
            payload["book_aligned_indicator_groups"],
            "book_aligned_indicator_groups",
        ),
        gap_items=_list_of_mappings(payload["gap_items"], "gap_items"),
        priority_recommendations=_list_of_mappings(
            payload["priority_recommendations"],
            "priority_recommendations",
        ),
        next_phases=_list_of_mappings(payload["next_phases"], "next_phases"),
    )


def _validate_groups(groups: list[dict[str, Any]]) -> None:
    _require_unique_ids(groups, "group_id", "book_aligned_indicator_groups")
    all_sensitivity_issues: list[dict[str, Any]] = []
    for group in groups:
        group_id = str(group.get("group_id") or "")
        _require_text(group, "display_name_zh", f"group {group_id}")
        _require_text(group, "purpose_zh", f"group {group_id}")
        status = str(group.get("current_coverage_status") or "")
        if status not in VALID_COVERAGE_STATUSES:
            raise BookIndicatorGapAnalysisError(
                f"group {group_id} current_coverage_status must be covered/partial/missing"
            )
        priority = str(group.get("implementation_priority") or "")
        if priority not in VALID_PRIORITIES:
            raise BookIndicatorGapAnalysisError(
                f"group {group_id} implementation_priority must be high/medium/low"
            )
        _non_empty_str_list(group.get("candidate_indicator_ids"), f"group {group_id}.candidate_indicator_ids")
        for issue in _list_of_mappings_allow_empty(group.get("sensitivity_issues")):
            all_sensitivity_issues.append(issue)
            _require_text(issue, "indicator_id", f"group {group_id}.sensitivity_issues")
            _require_text(issue, "observed_problem_zh", f"group {group_id}.sensitivity_issues")
            _require_text(issue, "example_scenario_id", f"group {group_id}.sensitivity_issues")
            _require_text(issue, "example_as_of", f"group {group_id}.sensitivity_issues")
            _require_text(issue, "candidate_fix_zh", f"group {group_id}.sensitivity_issues")
            if issue.get("whether_fix_should_be_scoring_change") is not False:
                raise BookIndicatorGapAnalysisError(
                    f"sensitivity issue {issue.get('indicator_id')} must not request scoring change in Phase 7D"
                )
            _require_text(issue, "recommended_next_step", f"group {group_id}.sensitivity_issues")
    _require_unique_ids(all_sensitivity_issues, "indicator_id", "sensitivity_issues")


def _validate_gap_items(items: list[dict[str, Any]]) -> None:
    _require_unique_ids(items, "gap_id", "gap_items")
    for item in items:
        _require_text(item, "display_name_zh", "gap_items")
        _require_text(item, "related_group_id", "gap_items")
        _require_text(item, "severity", "gap_items")
        _require_text(item, "description_zh", "gap_items")


def _validate_recommendations(items: list[dict[str, Any]]) -> None:
    _require_unique_ids(items, "recommendation_id", "priority_recommendations")
    for item in items:
        _require_text(item, "display_name_zh", "priority_recommendations")
        priority = str(item.get("priority") or "")
        if priority not in VALID_PRIORITIES:
            raise BookIndicatorGapAnalysisError("priority_recommendations priority must be high/medium/low")
        _require_text(item, "rationale_zh", "priority_recommendations")


def _validate_next_phases(items: list[dict[str, Any]]) -> None:
    _require_unique_ids(items, "phase_id", "next_phases")
    for item in items:
        _require_text(item, "title", "next_phases")


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BookIndicatorGapAnalysisError(f"Book indicator gap analysis file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BookIndicatorGapAnalysisError(
            f"Invalid YAML in book indicator gap analysis file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise BookIndicatorGapAnalysisError("Book indicator gap analysis YAML must be a mapping")
    return payload


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BookIndicatorGapAnalysisError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise BookIndicatorGapAnalysisError(f"{field} entries must be mappings")
    return mappings


def _list_of_mappings_allow_empty(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise BookIndicatorGapAnalysisError("sensitivity_issues must be a list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise BookIndicatorGapAnalysisError("sensitivity_issues entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BookIndicatorGapAnalysisError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise BookIndicatorGapAnalysisError(f"{field} entries must be non-empty")
    return items


def _require_unique_ids(items: list[dict[str, Any]], id_field: str, field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id:
            raise BookIndicatorGapAnalysisError(f"{field} entries must include {id_field}")
        if item_id in seen:
            raise BookIndicatorGapAnalysisError(f"{field} contains duplicate {id_field}: {item_id}")
        seen.add(item_id)


def _require_text(item: dict[str, Any], field: str, context: str) -> None:
    if not str(item.get(field) or ""):
        raise BookIndicatorGapAnalysisError(f"{context} entries must include non-empty {field}")
