from __future__ import annotations

from business_cycle.audits.model_freeze_semantics import (
    summarize_model_freeze_and_holdout_semantics,
)


def test_research_baseline_and_candidate_holdout_are_distinct() -> None:
    summary = summarize_model_freeze_and_holdout_semantics()

    assert summary["freeze_holdout_semantics_ready"] is True
    assert summary["research_baseline_freeze_valid"] is True
    assert summary["research_baseline_book_fidelity_complete"] is False
    assert summary["research_baseline_economically_validated"] is False
    assert summary["research_baseline_holdout_protocol_registered"] is True
    assert summary["book_faithful_scope_defined"] is True
    assert summary["book_faithful_candidate_model_implemented"] is False
    assert summary["book_faithful_candidate_model_frozen"] is False
    assert summary["book_faithful_candidate_holdout_registered"] is False
    assert summary["final_model_holdout_active"] is False
    assert summary["holdout_model_version_ambiguity_count"] == 0
    assert summary["premature_final_holdout_claim_count"] == 0
    assert summary["future_candidate_reuses_research_baseline_results"] is False

