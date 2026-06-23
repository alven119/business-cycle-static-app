from __future__ import annotations

from business_cycle.audits.phase11_book_core_phase_evidence_closure import (
    summarize_phase11_book_core_phase_evidence_closure,
)


def test_phase11_book_core_phase_evidence_closure_passes() -> None:
    summary = summarize_phase11_book_core_phase_evidence_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_document_present"] is True
    assert summary["north_star_contract_valid"] is True
    assert summary["phase_capability_mapping_complete"] is True
    assert summary["web_surface_mapping_complete"] is True
    assert summary["semantic_drift_count"] == 0
    assert summary["role_type_registry_ready"] is True
    assert summary["denominator_semantics_valid"] is True
    assert summary["evidence_rule_registry_ready"] is True
    assert summary["implemented_phase_evidence_evaluator_count"] > 0
    assert summary["new_phase_evidence_evaluable_role_count"] > 0
    assert summary["phase_evidence_partial_major_group_count"] > 0
    assert summary["retrospective_diagnostics_ready"] is True
    assert summary["phase_evidence_view_model_ready"] is True
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["candidate_capability_ready"] is False
    assert summary["formal_decision_model_ready"] is False
    assert summary["holdout_registered"] is False
    assert summary["development_next_phase"] == 12
    assert summary["prospective_track_next_action"] == "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
    assert summary["phase11_closure_status"] == (
        "closed_north_star_institutionalized_phase_evidence_runtime_expanded_"
        "candidate_model_disabled"
    )
