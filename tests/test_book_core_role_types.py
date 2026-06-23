from __future__ import annotations

from business_cycle.audits.book_core_role_types import (
    build_book_core_role_type_rows,
    summarize_book_core_role_types,
)


def test_book_core_role_types_cover_all_roles() -> None:
    summary = summarize_book_core_role_types()

    assert summary["canonical_requirement_count"] == 40
    assert summary["role_without_primary_type_count"] == 0
    assert summary["role_with_multiple_primary_types_count"] == 0
    assert summary["methodology_requirement_counted_as_indicator_count"] == 0
    assert summary["denominator_semantics_valid"] is True


def test_publication_lag_is_methodology_not_indicator_denominator() -> None:
    rows = {row["role_id"]: row for row in build_book_core_role_type_rows()}

    publication_lag = rows["recovery_publication_lag_awareness"]
    assert publication_lag["primary_role_type"] == "data_methodology_requirement"
    assert publication_lag["counts_in_indicator_denominator"] is False
    assert publication_lag["foundation_capability_id"] == (
        "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION"
    )
