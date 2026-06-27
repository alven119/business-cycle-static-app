from __future__ import annotations

from business_cycle.audits.phase42_north_star_product_alignment import (
    summarize_phase42_north_star_product_alignment,
)


def test_phase42_north_star_product_alignment() -> None:
    summary = summarize_phase42_north_star_product_alignment()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["phase42_addresses_current_stage_question"] is True
    assert summary["phase42_addresses_evidence_explanation_question"] is True
    assert summary["phase42_addresses_abstention_reason_question"] is True
    assert summary["current_phase_emitted"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["semantic_drift_count"] == 0
