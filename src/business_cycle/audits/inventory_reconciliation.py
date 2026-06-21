"""QA0 inventory reconciliation across repository inventory and audit specs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.repository_inventory import collect_repository_inventory


class InventoryReconciliationError(ValueError):
    """Raised when QA0 inventory reconciliation inputs are invalid."""


def run_qa0_inventory_reconciliation(root: str | Path = ".") -> dict[str, Any]:
    """Compare repository inventory to canonical requirements and audit mappings."""

    root_path = Path(root)
    inventory = collect_repository_inventory(root_path)
    manifest = _load_root(
        root_path / "specs/audits/canonical_book_requirement_manifest.yaml",
        "canonical_book_requirement_manifest",
    )
    traceability = _load_root(
        root_path / "specs/audits/book_method_traceability.yaml",
        "book_method_traceability",
    )
    coverage = _load_root(
        root_path / "specs/audits/book_indicator_coverage.yaml",
        "book_indicator_coverage",
    )
    lag_registry = _load_root(
        root_path / "specs/common/series_release_lag_registry.yaml",
        "series_release_lag_registry",
    )

    requirements = manifest.get("requirements", [])
    rows = traceability.get("rows", [])
    coverage_rows = coverage.get("indicators", [])
    registry_rows = lag_registry.get("series", [])

    requirement_ids = [str(row["requirement_id"]) for row in requirements]
    trace_ids = [str(row["requirement_id"]) for row in rows]
    required_coverage_ids = {
        str(row["requirement_id"])
        for row in requirements
        if bool(row.get("requires_indicator_coverage"))
    }
    coverage_requirement_ids = {
        str(row.get("coverage_requirement_id"))
        for row in coverage_rows
        if row.get("coverage_requirement_id")
    }

    inventory_items = inventory["items"]
    indicator_items = [
        item
        for item in inventory_items
        if item["inventory_type"] in {"formal_indicator", "experimental_indicator"}
    ]
    indicator_ids = {
        item["inventory_id"].removeprefix("indicator:") for item in indicator_items
    }
    coverage_indicator_ids = {str(row["indicator_id"]) for row in coverage_rows}
    mapped_indicator_ids = indicator_ids & coverage_indicator_ids

    discovered_series_ids = {
        item["inventory_id"].removeprefix("series:")
        for item in inventory_items
        if item["inventory_type"] in {"direct_series", "derived_series"}
    }
    registry_series_ids = {str(row["series_id"]) for row in registry_rows}
    audited_series_ids = discovered_series_ids & registry_series_ids
    registry_rows_by_id = {str(row["series_id"]): row for row in registry_rows}

    missing_traceability = set(requirement_ids) - set(trace_ids)
    unknown_traceability = set(trace_ids) - set(requirement_ids)
    duplicate_traceability = _duplicates(trace_ids)
    missing_book_indicator_coverage = required_coverage_ids - coverage_requirement_ids
    series_without_registry = discovered_series_ids - registry_series_ids
    series_without_temporal_status = {
        series_id
        for series_id in discovered_series_ids
        if not (
            registry_rows_by_id.get(series_id, {}).get("temporal_status")
            or registry_rows_by_id.get(series_id, {}).get("temporal_integrity_status")
        )
    }
    orphaned_paths = _orphaned_path_count(root_path, rows)
    taxonomy = _taxonomy_summary(requirements, rows)

    summary = {
        "canonical_requirement_count": len(requirement_ids),
        "traceability_row_count": len(trace_ids),
        "missing_traceability_requirement_count": len(missing_traceability),
        "duplicate_traceability_requirement_count": len(duplicate_traceability),
        "unknown_traceability_requirement_count": len(unknown_traceability),
        "discovered_formal_indicator_count": inventory["discovered_formal_indicator_count"],
        "discovered_experimental_indicator_count": inventory[
            "discovered_experimental_indicator_count"
        ],
        "discovered_unique_indicator_count": inventory[
            "discovered_unique_indicator_count"
        ],
        "mapped_indicator_count": len(mapped_indicator_ids),
        "unmapped_indicator_count": len(indicator_ids - coverage_indicator_ids),
        "discovered_direct_series_count": inventory["discovered_direct_series_count"],
        "discovered_derived_series_count": inventory["discovered_derived_series_count"],
        "discovered_unique_series_count": len(discovered_series_ids),
        "audited_series_count": len(audited_series_ids),
        "unaudited_series_count": len(discovered_series_ids - audited_series_ids),
        "release_lag_registry_series_count": len(registry_series_ids),
        "series_without_release_lag_registry_count": len(series_without_registry),
        "series_without_temporal_status_count": len(series_without_temporal_status),
        "provenance_mapped_indicator_count": len(mapped_indicator_ids),
        "provenance_unmapped_indicator_count": len(indicator_ids - coverage_indicator_ids),
        "orphaned_implementation_path_count": orphaned_paths,
        "duplicate_inventory_id_count": inventory["duplicate_inventory_id_count"],
        "duplicate_series_alias_count": inventory["duplicate_series_alias_count"],
        "canonical_book_indicator_requirement_count": len(required_coverage_ids),
        "phase_role_indicator_coverage_row_count": len(coverage_rows),
        "book_indicator_manifest_count": len(required_coverage_ids),
        "book_indicator_coverage_row_count": len(coverage_requirement_ids),
        "missing_book_indicator_coverage_row_count": len(missing_book_indicator_coverage),
        "hard_coded_summary_value_count": _hard_coded_summary_value_count(root_path),
        **taxonomy,
    }
    summary["qa0_inventory_complete"] = all(
        summary[field] == 0
        for field in (
            "missing_traceability_requirement_count",
            "duplicate_traceability_requirement_count",
            "unknown_traceability_requirement_count",
            "unmapped_indicator_count",
            "unaudited_series_count",
            "series_without_release_lag_registry_count",
            "series_without_temporal_status_count",
            "provenance_unmapped_indicator_count",
            "orphaned_implementation_path_count",
            "duplicate_inventory_id_count",
            "duplicate_series_alias_count",
            "missing_book_indicator_coverage_row_count",
            "hard_coded_summary_value_count",
            "taxonomy_misclassification_count",
            "modern_methodology_marked_book_core_count",
            "duplicate_finding_id_count",
            "duplicate_requirement_finding_count",
        )
    )
    return summary


def _load_root(path: Path, root_key: str) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get(root_key), dict):
        raise InventoryReconciliationError(f"{path} must contain root mapping {root_key}")
    return payload[root_key]


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _taxonomy_summary(
    requirements: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> dict[str, int]:
    allowed_sources = {
        "book",
        "official_data_semantics",
        "modern_quant_methodology",
        "project_safety",
    }
    allowed_fidelity = {"book_core", "book_supporting", "not_book_requirement"}
    allowed_criticality = {"P0", "P1", "P2", "informational"}
    taxonomy_misclassification = 0
    for item in [*requirements, *rows]:
        source = item.get("source_authority")
        fidelity = item.get("book_fidelity_class") or item.get("fidelity_class")
        criticality = item.get("readiness_criticality")
        if source not in allowed_sources:
            taxonomy_misclassification += 1
        if fidelity not in allowed_fidelity:
            taxonomy_misclassification += 1
        if criticality not in allowed_criticality:
            taxonomy_misclassification += 1
        if source != "book" and fidelity == "book_core":
            taxonomy_misclassification += 1
        if item.get("requirement_id") in {
            "untouched_holdout_required",
            "parameter_freeze_before_holdout",
        } and fidelity == "book_core":
            taxonomy_misclassification += 1

    finding_ids: list[str] = []
    requirement_finding_keys: list[str] = []
    for row in rows:
        for finding in row.get("findings", []):
            finding_id = str(finding.get("finding_id", ""))
            requirement_id = str(finding.get("requirement_id", ""))
            finding_type = str(finding.get("finding_type", ""))
            severity = str(finding.get("severity", ""))
            blocking_gate_id = str(finding.get("blocking_gate_id", ""))
            if not all((finding_id, requirement_id, finding_type, severity, blocking_gate_id)):
                taxonomy_misclassification += 1
            finding_ids.append(finding_id)
            requirement_finding_keys.append(f"{requirement_id}::{finding_id}")

    modern_book_core = [
        item
        for item in [*requirements, *rows]
        if item.get("source_authority") == "modern_quant_methodology"
        and (item.get("book_fidelity_class") or item.get("fidelity_class")) == "book_core"
    ]
    return {
        "book_sourced_requirement_count": len(
            [item for item in requirements if item.get("source_authority") == "book"]
        ),
        "official_data_semantics_requirement_count": len(
            [
                item
                for item in requirements
                if item.get("source_authority") == "official_data_semantics"
            ]
        ),
        "modern_methodology_requirement_count": len(
            [
                item
                for item in requirements
                if item.get("source_authority") == "modern_quant_methodology"
            ]
        ),
        "project_safety_requirement_count": len(
            [item for item in requirements if item.get("source_authority") == "project_safety"]
        ),
        "book_core_requirement_count": len(
            [item for item in requirements if item.get("book_fidelity_class") == "book_core"]
        ),
        "book_supporting_requirement_count": len(
            [
                item
                for item in requirements
                if item.get("book_fidelity_class") == "book_supporting"
            ]
        ),
        "not_book_requirement_count": len(
            [
                item
                for item in requirements
                if item.get("book_fidelity_class") == "not_book_requirement"
            ]
        ),
        "modern_methodology_marked_book_core_count": len(modern_book_core),
        "taxonomy_misclassification_count": taxonomy_misclassification,
        "duplicate_finding_id_count": len(_duplicates(finding_ids)),
        "duplicate_requirement_finding_count": len(_duplicates(requirement_finding_keys)),
    }


def _orphaned_path_count(root: Path, rows: list[dict[str, Any]]) -> int:
    count = 0
    allowed_missing = {"missing", "none", "not_applicable"}
    for row in rows:
        for field in ("implementation_paths", "test_paths"):
            for raw_path in row.get(field, []):
                path_text = str(raw_path)
                if path_text in allowed_missing:
                    continue
                if not (root / path_text).exists():
                    count += 1
    return count


def _hard_coded_summary_value_count(root: Path) -> int:
    source = (root / "src/business_cycle/audits/qa0_integrity_audit.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "traceability_row_count" + "\": 22",
        "audited_series_count" + "\": 8",
        "book_indicator_count" + "\": 14",
        "p0_finding_count" + "\": 18",
        "p1_finding_count" + "\": 11",
    )
    return sum(pattern in source for pattern in forbidden)
