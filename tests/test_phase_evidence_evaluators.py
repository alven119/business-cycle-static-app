from __future__ import annotations

from business_cycle.shadow_model.phase_evidence_evaluators import (
    build_phase_evidence_evaluator_contracts,
    evaluate_phase_evidence,
    summarize_phase_evidence_evaluators,
)


def test_phase_evidence_evaluators_are_shadow_only() -> None:
    summary = summarize_phase_evidence_evaluators()

    assert summary["implemented_phase_evidence_evaluator_count"] > 0
    assert summary["new_phase_evidence_evaluable_role_count"] > 0
    assert summary["implementation_failed_role_count"] == 0
    assert summary["new_candidate_selection_eligible_role_count"] == 0
    assert summary["new_numeric_threshold_count"] == 0
    assert summary["new_weight_count"] == 0


def test_safe_role_emits_phase_evidence_without_candidate_phase() -> None:
    result = evaluate_phase_evidence(
        role_id="recovery_real_retail_sales",
        as_of="2019-12-31",
        data_mode="revised",
    )

    assert result["phase_evidence_output_available"] is True
    assert result["supportive"] is True
    assert result["candidate_phase_emitted"] is False
    assert result["current_phase_emitted"] is False
    assert result["numeric_threshold_used"] is False
    assert result["numeric_weight_used"] is False


def test_unresolved_qualitative_rule_does_not_emit_evidence() -> None:
    result = evaluate_phase_evidence(
        role_id="growth_sustainable_inflation_interpretation",
        as_of="2019-12-31",
        data_mode="revised",
    )

    assert result["phase_evidence_output_available"] is False
    assert result["abstention_reason"] == "phase_evidence_rule_not_operational"


def test_all_contracts_have_no_candidate_or_current_phase_output() -> None:
    for contract in build_phase_evidence_evaluator_contracts():
        assert contract["candidate_selection_eligible"] is False
        assert contract["current_phase_output_allowed"] is False
        assert contract["numeric_threshold"] is None
        assert contract["numeric_weight"] is None
