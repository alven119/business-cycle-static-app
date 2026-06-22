from __future__ import annotations

from business_cycle.audits.qa5_book_core_shadow_model_closure import (
    summarize_qa5_book_core_shadow_model_closure,
)


def test_qa5_closure_passes_with_explicit_data_gaps() -> None:
    summary = summarize_qa5_book_core_shadow_model_closure()

    assert summary["result"] == "passed"
    assert summary["scope_count_semantics_ready"] is True
    assert summary["book_core_data_contract_registry_ready"] is True
    assert summary["shadow_evidence_model_implemented"] is True
    assert summary["production_isolation_verified"] is True
    assert summary["formal_candidate_phase_computed"] is False
    assert summary["formal_decision_model_ready"] is False
    assert summary["production_book_fidelity_ready"] is False
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["proposed_v2_economically_validated"] is False
    assert summary["holdout_registered"] is False
    assert summary["qa6_allowed"] is True
    assert summary["recommended_next_phase"] == "QA6"
    assert summary["qa5_closure_status"] == "closed_shadow_evidence_model_ready_with_explicit_data_gaps"
