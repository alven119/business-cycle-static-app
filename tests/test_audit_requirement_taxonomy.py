from __future__ import annotations

import copy

import yaml

from business_cycle.audits.inventory_reconciliation import (
    _taxonomy_summary,
    run_qa0_inventory_reconciliation,
)


def test_modern_methodology_is_not_book_core() -> None:
    summary = run_qa0_inventory_reconciliation()

    assert summary["modern_methodology_marked_book_core_count"] == 0
    assert summary["taxonomy_misclassification_count"] == 0
    assert summary["book_core_requirement_count"] < summary["canonical_requirement_count"]


def test_indicator_requirement_and_phase_role_counts_are_separate() -> None:
    summary = run_qa0_inventory_reconciliation()

    assert summary["canonical_book_indicator_requirement_count"] == 40
    assert summary["phase_role_indicator_coverage_row_count"] == 63


def test_duplicate_finding_id_is_detected() -> None:
    payload = yaml.safe_load(
        open("specs/audits/book_method_traceability.yaml", encoding="utf-8")
    )
    rows = payload["book_method_traceability"]["rows"]
    mutated = copy.deepcopy(rows)
    first_with_finding = next(row for row in mutated if row["findings"])
    second_with_finding = next(
        row for row in mutated if row["findings"] and row is not first_with_finding
    )
    second_with_finding["findings"][0]["finding_id"] = first_with_finding["findings"][0][
        "finding_id"
    ]

    summary = _taxonomy_summary([], mutated)

    assert summary["duplicate_finding_id_count"] == 1
