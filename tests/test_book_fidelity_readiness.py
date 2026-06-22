from __future__ import annotations

from business_cycle.audits.book_fidelity_readiness import (
    summarize_book_fidelity_readiness,
)


def test_book_fidelity_readiness_rollups_are_layered() -> None:
    summary = summarize_book_fidelity_readiness()

    assert summary["book_fidelity_rollups_ready"] is True
    assert summary["major_group_shadow_evidence_coverage_ratio"] > 0
    assert summary["formal_decision_model_ready"] is False
    assert summary["production_book_fidelity_ready"] is False
    assert summary["book_alignment_claim_allowed"] is False

