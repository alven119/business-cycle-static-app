from __future__ import annotations

from business_cycle.audits.qa8_book_explicit_evaluator_closure import (
    summarize_qa8_book_explicit_evaluator_closure,
)


def test_qa8_book_explicit_evaluator_closure_passes() -> None:
    summary = summarize_qa8_book_explicit_evaluator_closure()

    assert summary["result"] == "passed"
    assert summary["blocker_accounting_reconciled"] is True
    assert summary["explicit_rule_eligibility_ready"] is True
    assert summary["book_explicit_evaluators_implemented"] is True
    assert summary["evaluator_metamorphic_coverage_ready"] is True
    assert summary["retrospective_evidence_diagnostics_ready"] is True
    assert summary["prospective_protocol_registered"] is True
    assert summary["prospective_clock_gate_ready"] is True
    assert summary["evaluator_freeze_ready"] is True
    assert summary["production_isolation_verified"] is True
    assert summary["formal_decision_model_ready"] is False
    assert summary["holdout_registered"] is False
    assert summary["recommended_next_phase"] == "QA9"
    assert (
        summary["qa8_closure_status"]
        == "closed_book_explicit_evaluators_frozen_forward_protocol_registered_not_started"
    )
