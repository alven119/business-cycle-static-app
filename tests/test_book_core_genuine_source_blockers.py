from __future__ import annotations

from business_cycle.audits.book_core_genuine_source_blockers import (
    build_genuine_source_blocker_rows,
    summarize_genuine_source_blockers,
)


def test_genuine_source_blockers_have_evidence_and_resolution_triggers() -> None:
    summary = summarize_genuine_source_blockers()
    rows = build_genuine_source_blocker_rows()

    assert summary["genuine_blocker_register_ready"] is True
    assert summary["genuine_blocker_count"] == 5
    assert summary["implementation_bug_misclassified_as_blocker_count"] == 0
    assert summary["blocker_without_evidence_count"] == 0
    assert summary["blocker_without_resolution_trigger_count"] == 0
    assert summary["unsafe_substitution_proposed_count"] == 0
    assert {row["role_id"] for row in rows} == {
        "recovery_publication_lag_awareness",
        "growth_real_disposable_income_vs_consumption",
        "growth_adp_employment",
        "growth_sustainable_inflation_interpretation",
        "boom_consumer_confidence",
    }
