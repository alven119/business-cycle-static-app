from __future__ import annotations

from business_cycle.audits.book_core_transformations import (
    build_book_core_transformation_contracts,
    summarize_book_core_transformation_contracts,
)


def test_transformation_contracts_define_no_new_threshold_or_weight() -> None:
    summary = summarize_book_core_transformation_contracts()

    assert summary["transformation_contract_registry_ready"] is True
    assert summary["transformation_contract_count"] == 40
    assert summary["new_threshold_defined_count"] == 0
    assert summary["new_weight_defined_count"] == 0
    assert summary["engineering_default_mislabeled_as_book_count"] == 0
    assert summary["strict_transform_with_revised_lookback_count"] == 0


def test_roles_requiring_new_threshold_are_raw_transform_only() -> None:
    rows = build_book_core_transformation_contracts()
    prereg = [row for row in rows if row["threshold_status"] == "requires_preregistration"]

    assert prereg
    assert all(row["shadow_execution_mode"] == "raw_transform_only" for row in prereg)

