"""QA4 book-faithful formal scope contract."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml


DEFAULT_SCOPE_PATH = Path("specs/audits/book_faithful_formal_model_scope.yaml")
MANIFEST_PATH = Path("specs/audits/canonical_book_requirement_manifest.yaml")
TRACEABILITY_PATH = Path("specs/audits/book_method_traceability.yaml")
COVERAGE_PATH = Path("specs/audits/book_indicator_coverage.yaml")

STATUS_MAP = {
    "formal": "formal_v1",
    "experimental": "experimental",
    "spec_only": "spec_only",
    "missing": "missing",
    "conflicting": "conflicting",
}


def build_book_faithful_scope_items() -> list[dict[str, Any]]:
    """Expand canonical requirements into one QA4 scope item per requirement."""

    manifest = _load_manifest()
    traceability = {
        row["requirement_id"]: row for row in _load_traceability()["rows"]
    }
    coverage = {
        row["coverage_requirement_id"]: row
        for row in _load_coverage()["indicators"]
        if row.get("coverage_requirement_id")
    }
    items: list[dict[str, Any]] = []
    for requirement in manifest:
        requirement_id = requirement["requirement_id"]
        trace = traceability[requirement_id]
        coverage_row = coverage.get(requirement_id)
        current_status = STATUS_MAP[trace["implementation_status"]]
        role = _role_for(requirement)
        current_paths = [
            path
            for path in trace.get("implementation_paths", [])
            if path and path != "missing"
        ]
        if coverage_row and coverage_row.get("formal_or_experimental") == "missing":
            current_status = "missing"
        item = {
            "scope_item_id": f"scope::{requirement_id}",
            "book_requirement_id": requirement_id,
            "phase_or_layer": requirement["group"],
            "book_section": requirement["book_section"],
            "book_page_reference": requirement["book_page_reference"],
            "requirement_zh": requirement["requirement_zh"],
            "book_fidelity_class": requirement["book_fidelity_class"],
            "role": role,
            "required_for_minimum_book_fidelity": requirement[
                "book_fidelity_class"
            ]
            == "book_core",
            "required_for_complete_book_fidelity": requirement[
                "book_fidelity_class"
            ]
            in {"book_core", "book_supporting"},
            "current_implementation_status": current_status,
            "current_paths": current_paths,
            "current_indicator_ids": _indicator_ids(coverage_row),
            "current_series_ids": _series_ids(coverage_row),
            "proposed_v2_role": role,
            "promotion_required": current_status != "formal_v1",
            "temporal_data_ready": _temporal_ready(coverage_row, current_status),
            "decision_rule_ready": current_status == "formal_v1",
            "unresolved_reason": _unresolved_reason(trace, coverage_row, current_status),
            "blocking_severity": trace.get("blocking_severity", "none"),
            "recommended_work_package": _work_package(requirement, current_status),
        }
        items.append(item)
    return items


def summarize_book_faithful_formal_model_scope(
    path: str | Path = DEFAULT_SCOPE_PATH,
) -> dict[str, Any]:
    """Return formal scope counts and book-fidelity gates."""

    spec = _load_scope_spec(path)
    items = build_book_faithful_scope_items()
    counts = Counter(item["book_fidelity_class"] for item in items)
    status_counts = Counter(item["current_implementation_status"] for item in items)
    min_required = [
        item for item in items if item["required_for_minimum_book_fidelity"]
    ]
    min_ready = [
        item
        for item in min_required
        if item["current_implementation_status"] == "formal_v1"
    ]
    complete_required = [
        item for item in items if item["required_for_complete_book_fidelity"]
    ]
    complete_ready = [
        item
        for item in complete_required
        if item["current_implementation_status"] == "formal_v1"
    ]
    ids = [item["book_requirement_id"] for item in items]
    book_core_manifest_ids = {
        row["requirement_id"]
        for row in _load_manifest()
        if row["book_fidelity_class"] == "book_core"
    }
    mapped_core_ids = {
        item["book_requirement_id"]
        for item in items
        if item["book_fidelity_class"] == "book_core"
    }
    duplicate_ids = {item_id for item_id, count in Counter(ids).items() if count > 1}
    one_to_one_core = mapped_core_ids == book_core_manifest_ids and not duplicate_ids
    complete = all(
        item["current_implementation_status"] == "formal_v1"
        for item in complete_required
    )
    return {
        "phase": "QA4",
        "book_faithful_scope_contract_ready": bool(
            spec["generation_policy"]["one_scope_item_per_canonical_requirement"]
        )
        and one_to_one_core,
        "formal_scope_item_count": len(items),
        "book_core_scope_item_count": counts["book_core"],
        "book_supporting_scope_item_count": counts["book_supporting"],
        "modern_extension_scope_item_count": counts["not_book_requirement"],
        "current_formal_v1_scope_item_count": status_counts["formal_v1"],
        "experimental_scope_item_count": status_counts["experimental"],
        "spec_only_scope_item_count": status_counts["spec_only"],
        "missing_scope_item_count": status_counts["missing"],
        "conflicting_scope_item_count": status_counts["conflicting"],
        "modern_substitute_scope_item_count": status_counts["modern_substitute"],
        "minimum_book_fidelity_required_count": len(min_required),
        "minimum_book_fidelity_ready_count": len(min_ready),
        "minimum_book_fidelity_coverage_ratio": _ratio(len(min_ready), len(min_required)),
        "complete_book_fidelity_ready_count": len(complete_ready),
        "complete_book_fidelity_coverage_ratio": _ratio(
            len(complete_ready), len(complete_required)
        ),
        "book_faithful_scope_complete": complete,
        "minimum_book_fidelity_ready": len(min_ready) == len(min_required),
        "complete_book_fidelity_ready": complete,
        "book_alignment_claim_allowed": False,
        "duplicate_scope_requirement_id_count": len(duplicate_ids),
        "missing_book_core_scope_item_count": len(book_core_manifest_ids - mapped_core_ids),
        "scope_items": items,
        "unresolved_book_core_items": [
            item
            for item in items
            if item["book_fidelity_class"] == "book_core"
            and item["current_implementation_status"] != "formal_v1"
        ],
    }


def summarize_phase_scope(group: str) -> dict[str, Any]:
    """Return status counts for a canonical requirement group."""

    items = [
        item
        for item in build_book_faithful_scope_items()
        if item["phase_or_layer"] == group
    ]
    counts = Counter(item["current_implementation_status"] for item in items)
    return {
        "role_count": len(items),
        "formal_v1_ready_count": counts["formal_v1"],
        "experimental_ready_count": counts["experimental"],
        "spec_only_count": counts["spec_only"],
        "missing_count": counts["missing"],
        "conflicting_count": counts["conflicting"],
        "minimum_scope_ready": bool(items)
        and all(item["current_implementation_status"] == "formal_v1" for item in items),
        "items": items,
    }


def summarize_recovery_formal_scope() -> dict[str, Any]:
    """Return QA4 recovery scope status."""

    summary = summarize_phase_scope("recovery_indicators")
    return {
        "phase": "QA4",
        "recovery_scope_ready": summary["role_count"] == 10,
        "recovery_book_core_role_count": summary["role_count"],
        "recovery_formal_v1_ready_count": summary["formal_v1_ready_count"],
        "recovery_experimental_ready_count": summary["experimental_ready_count"],
        "recovery_missing_count": summary["missing_count"],
        "recovery_modern_substitute_count": 0,
        "recovery_minimum_scope_ready": summary["minimum_scope_ready"],
        "items": summary["items"],
    }


def summarize_growth_formal_scope() -> dict[str, Any]:
    """Return QA4 growth scope status."""

    summary = summarize_phase_scope("growth_indicators")
    data_contract_blocked = [
        item for item in summary["items"] if "adp" in item["book_requirement_id"]
    ]
    return {
        "phase": "QA4",
        "growth_scope_ready": summary["role_count"] == 10,
        "growth_book_core_role_count": summary["role_count"],
        "growth_formal_v1_ready_count": summary["formal_v1_ready_count"],
        "growth_experimental_ready_count": summary["experimental_ready_count"],
        "growth_missing_count": summary["missing_count"],
        "growth_data_contract_blocked_count": len(data_contract_blocked),
        "growth_minimum_scope_ready": summary["minimum_scope_ready"],
        "items": summary["items"],
    }


def summarize_boom_formal_scope() -> dict[str, Any]:
    """Return QA4 boom scope status."""

    summary = summarize_phase_scope("boom_ending_indicators")
    return {
        "phase": "QA4",
        "boom_scope_ready": summary["role_count"] == 11,
        "boom_book_core_role_count": summary["role_count"],
        "boom_formal_v1_ready_count": summary["formal_v1_ready_count"],
        "boom_experimental_ready_count": summary["experimental_ready_count"],
        "boom_missing_count": summary["missing_count"],
        "boom_modern_extension_count": 0,
        "boom_minimum_scope_ready": summary["minimum_scope_ready"],
        "items": summary["items"],
    }


def summarize_recession_trough_formal_scope() -> dict[str, Any]:
    """Return QA4 recession confirmation and trough scope status."""

    summary = summarize_phase_scope("recession_trough_requirements")
    confirmation = [
        item
        for item in summary["items"]
        if item["book_requirement_id"].startswith("recession_")
    ]
    trough = [
        item
        for item in summary["items"]
        if item["book_requirement_id"].startswith("trough_")
    ]
    recovery_watch_support = [
        item
        for item in summary["items"]
        if "policy_financial" in item["book_requirement_id"]
    ]
    return {
        "phase": "QA4",
        "recession_trough_scope_ready": summary["role_count"] == 9,
        "recession_confirmation_core_role_count": len(confirmation),
        "recession_trough_core_role_count": len(trough),
        "recovery_watch_supporting_role_count": len(recovery_watch_support),
        "formal_v1_ready_count": summary["formal_v1_ready_count"],
        "experimental_ready_count": summary["experimental_ready_count"],
        "missing_count": summary["missing_count"],
        "minimum_scope_ready": summary["minimum_scope_ready"],
        "items": summary["items"],
    }


def _load_scope_spec(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload["book_faithful_formal_model_scope"]


def _load_manifest() -> list[dict[str, Any]]:
    payload = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    return payload["canonical_book_requirement_manifest"]["requirements"]


def _load_traceability() -> dict[str, Any]:
    return yaml.safe_load(TRACEABILITY_PATH.read_text(encoding="utf-8"))[
        "book_method_traceability"
    ]


def _load_coverage() -> dict[str, Any]:
    return yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))[
        "book_indicator_coverage"
    ]


def _role_for(requirement: dict[str, Any]) -> str:
    group = requirement["group"]
    requirement_type = requirement["requirement_type"]
    if group == "cycle_rules":
        return "phase_core"
    if group in {"recovery_indicators", "growth_indicators", "boom_ending_indicators"}:
        return "phase_core" if requirement["book_fidelity_class"] == "book_core" else "phase_supporting"
    if group == "recession_trough_requirements":
        return "transition_evidence"
    if group == "long_cycle_regime":
        return "regime_evidence"
    if requirement_type == "portfolio_rule":
        return "portfolio_rule"
    return "data_methodology"


def _indicator_ids(coverage_row: dict[str, Any] | None) -> list[str]:
    if not coverage_row or coverage_row.get("formal_or_experimental") == "missing":
        return []
    return [coverage_row["indicator_id"]]


def _series_ids(coverage_row: dict[str, Any] | None) -> list[str]:
    if not coverage_row or coverage_row.get("formal_or_experimental") == "missing":
        return []
    return [coverage_row["series_id"]]


def _temporal_ready(coverage_row: dict[str, Any] | None, status: str) -> bool:
    if status != "formal_v1":
        return False
    if coverage_row is None:
        return True
    return coverage_row.get("vintage_support") not in {"missing", None}


def _unresolved_reason(
    trace: dict[str, Any],
    coverage_row: dict[str, Any] | None,
    status: str,
) -> str:
    if status == "formal_v1":
        return "none"
    if coverage_row and coverage_row.get("missing_reason"):
        return str(coverage_row["missing_reason"])
    return str(trace.get("divergence_from_book") or "scope not formal-ready")


def _work_package(requirement: dict[str, Any], status: str) -> str:
    if status == "formal_v1":
        return "preserve_current_contract"
    group = requirement["group"]
    if group == "growth_indicators":
        return "QA5_growth_book_core_data_contract"
    if group == "boom_ending_indicators":
        return "QA5_boom_book_core_data_contract"
    if group == "recovery_indicators":
        return "QA5_recovery_temporal_and_role_remediation"
    if group == "recession_trough_requirements":
        return "QA5_recession_trough_shadow_formal_model"
    if group == "long_cycle_regime":
        return "future_secular_regime_scope_implementation"
    if "portfolio" in group or "benchmark" in group:
        return "future_book_portfolio_benchmark_contract"
    return "QA5_formal_scope_remediation"


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)
