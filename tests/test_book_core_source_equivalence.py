from __future__ import annotations

from business_cycle.audits.source_equivalence import (
    build_source_equivalence_review_rows,
    summarize_source_equivalence_reviews,
)


def test_book_core_source_equivalence_reviews_block_unsafe_substitutes() -> None:
    summary = summarize_source_equivalence_reviews()
    rows = build_source_equivalence_review_rows()

    assert summary["source_equivalence_reviews_ready"] is True
    assert summary["equivalence_review_count"] == 40
    assert summary["unverified_count"] == 0
    assert summary["alternative_used_without_equivalence_review_count"] == 0
    assert summary["supporting_source_used_as_core_count"] == 0
    assert any(
        row["role_id"] == "boom_consumer_confidence"
        and row["equivalence_status"] == "not_equivalent"
        and row["used_as_core"] is False
        for row in rows
    )
