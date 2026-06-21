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
        if not registry_rows_by_id.get(series_id, {}).get("temporal_integrity_status")
    }
    orphaned_paths = _orphaned_path_count(root_path, rows)

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
        "book_indicator_manifest_count": len(required_coverage_ids),
        "book_indicator_coverage_row_count": len(coverage_requirement_ids),
        "missing_book_indicator_coverage_row_count": len(missing_book_indicator_coverage),
        "hard_coded_summary_value_count": _hard_coded_summary_value_count(root_path),
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
