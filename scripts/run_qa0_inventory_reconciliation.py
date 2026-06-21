#!/usr/bin/env python
"""Run QA0 inventory reconciliation."""

from __future__ import annotations

from business_cycle.audits.audit_implementation_integrity import (
    summarize_audit_implementation_integrity,
)
from business_cycle.audits.inventory_reconciliation import run_qa0_inventory_reconciliation


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def main() -> int:
    summary = run_qa0_inventory_reconciliation()
    integrity = summarize_audit_implementation_integrity()
    summary = {**summary, **integrity}
    keys = (
        "canonical_requirement_count",
        "traceability_row_count",
        "missing_traceability_requirement_count",
        "duplicate_traceability_requirement_count",
        "unknown_traceability_requirement_count",
        "discovered_formal_indicator_count",
        "discovered_experimental_indicator_count",
        "discovered_unique_indicator_count",
        "mapped_indicator_count",
        "unmapped_indicator_count",
        "discovered_direct_series_count",
        "discovered_derived_series_count",
        "discovered_unique_series_count",
        "audited_series_count",
        "unaudited_series_count",
        "release_lag_registry_series_count",
        "series_without_release_lag_registry_count",
        "series_without_temporal_status_count",
        "provenance_mapped_indicator_count",
        "provenance_unmapped_indicator_count",
        "orphaned_implementation_path_count",
        "duplicate_inventory_id_count",
        "duplicate_series_alias_count",
        "book_sourced_requirement_count",
        "official_data_semantics_requirement_count",
        "modern_methodology_requirement_count",
        "project_safety_requirement_count",
        "book_core_requirement_count",
        "book_supporting_requirement_count",
        "not_book_requirement_count",
        "modern_methodology_marked_book_core_count",
        "taxonomy_misclassification_count",
        "canonical_book_indicator_requirement_count",
        "phase_role_indicator_coverage_row_count",
        "duplicate_finding_id_count",
        "duplicate_requirement_finding_count",
        "book_indicator_manifest_count",
        "book_indicator_coverage_row_count",
        "missing_book_indicator_coverage_row_count",
        "hard_coded_summary_value_count",
        "inventory_drift_detection_ready",
        "traceability_drift_detection_ready",
        "series_drift_detection_ready",
        "provenance_drift_detection_ready",
        "qa0_inventory_complete",
    )
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["qa0_inventory_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
