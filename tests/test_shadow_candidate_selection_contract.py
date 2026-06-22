from __future__ import annotations

from business_cycle.shadow_model.candidate_selection import (
    select_shadow_candidate,
    summarize_shadow_candidate_selection_contract,
)


def test_shadow_candidate_selection_contract_has_no_weight_or_tie_break() -> None:
    summary = summarize_shadow_candidate_selection_contract()

    assert summary["candidate_selection_contract_ready"] is True
    assert summary["numeric_weight_in_candidate_selection_count"] == 0
    assert summary["equal_weight_in_candidate_selection_count"] == 0
    assert summary["role_count_vote_count"] == 0
    assert summary["arbitrary_phase_priority_count"] == 0
    assert summary["transition_evidence_used_for_selection_count"] == 0
    assert summary["regime_evidence_used_for_selection_count"] == 0
    assert summary["external_context_used_for_selection_count"] == 0
    assert summary["known_label_used_for_selection_count"] == 0


def test_shadow_candidate_selection_preserves_ambiguity() -> None:
    result = select_shadow_candidate(
        [
            {"phase_id": "recovery", "aggregation_eligible": True},
            {"phase_id": "growth", "aggregation_eligible": True},
        ]
    )

    assert result["candidate_selection_status"] == "ambiguous_multiple_candidates"
    assert result["selected_candidate_phase"] is None


def test_shadow_candidate_selection_rejects_forbidden_inputs() -> None:
    result = select_shadow_candidate(
        [{"phase_id": "recovery", "aggregation_eligible": True}],
        forbidden_inputs=["external_context_prior"],
    )

    assert result["candidate_selection_status"] == "abstained_rule_unresolved"
    assert result["selected_candidate_phase"] is None
