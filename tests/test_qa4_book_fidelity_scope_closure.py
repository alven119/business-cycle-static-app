from __future__ import annotations

from business_cycle.audits.qa4_book_fidelity_scope_closure import (
    summarize_qa4_book_fidelity_scope_closure,
)


def test_qa4_closure_contract_passes_scope_governance() -> None:
    summary = summarize_qa4_book_fidelity_scope_closure()

    assert summary["result"] == "passed"
    assert summary["formal_model_layer_architecture_ready"] is True
    assert summary["book_faithful_scope_contract_ready"] is True
    assert summary["indicator_scope_matrix_ready"] is True
    assert summary["formal_scope_freeze_ready"] is True
    assert summary["book_faithful_scope_complete"] is False
    assert summary["complete_book_fidelity_ready"] is False
    assert summary["production_v1_book_alignment_claim_allowed"] is False
    assert summary["proposed_v2_implemented"] is False
    assert summary["proposed_v2_holdout_registered"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["scoring_weight_change_count"] == 0
    assert summary["threshold_change_count"] == 0
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
    assert summary["qa5_allowed"] is True
    assert summary["recommended_next_phase"] == "QA5"
    assert summary["qa4_closure_status"] == "closed_formal_scope_defined_not_implemented"

