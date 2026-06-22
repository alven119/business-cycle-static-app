from __future__ import annotations

from business_cycle.audits.qa5_scope_count_semantics import (
    summarize_qa5_scope_count_semantics,
)


def test_formal_v1_primary_partition_is_mutually_exclusive() -> None:
    summary = summarize_qa5_scope_count_semantics()

    assert summary["scope_count_semantics_ready"] is True
    assert summary["formal_v1_indicator_count"] == 13
    assert summary["formal_v1_primary_partition_sum"] == 13
    assert summary["formal_v1_primary_partition_valid"] is True
    assert summary["overlapping_primary_classification_count"] == 0
    assert summary["duplicate_indicator_matrix_row_count"] == 0
    assert summary["canonical_role_without_matrix_row_count"] == 0
    assert summary["matrix_row_without_canonical_or_existing_identity_count"] == 0


def test_canonical_counts_are_separated_from_indicator_rows() -> None:
    summary = summarize_qa5_scope_count_semantics()

    assert summary["book_core_requirement_count"] == 77
    assert summary["canonical_book_indicator_role_count"] == 40
    assert summary["existing_unique_indicator_count"] == 38
    assert summary["missing_book_core_role_count"] == 16
    assert summary["indicator_matrix_row_identity_count"] == 54

