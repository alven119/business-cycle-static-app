from __future__ import annotations

from business_cycle.audits.qa7_evidence_rule_candidate_freeze_closure import (
    summarize_qa7_evidence_rule_candidate_freeze_closure,
)


def test_qa7_evidence_rule_candidate_freeze_closure_passes() -> None:
    summary = summarize_qa7_evidence_rule_candidate_freeze_closure()

    assert summary["result"] == "passed"
    assert summary["evidence_rule_provenance_ready"] is True
    assert summary["role_evaluation_contract_registry_ready"] is True
    assert summary["candidate_selection_contract_ready"] is True
    assert summary["synthetic_candidate_selection_validated"] is True
    assert summary["candidate_selection_freeze_ready"] is True
    assert summary["production_isolation_verified"] is True
    assert summary["formal_candidate_phase_computed_on_real_data"] is False
    assert summary["formal_decision_model_ready"] is False
    assert summary["holdout_registered"] is False
    assert summary["qa8_allowed"] is True
    assert summary["recommended_next_phase"] == "QA8"
    assert (
        summary["qa7_closure_status"]
        == "closed_evidence_rules_preregistered_real_candidate_selection_disabled"
    )
