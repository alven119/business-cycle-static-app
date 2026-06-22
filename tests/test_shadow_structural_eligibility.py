from __future__ import annotations

from business_cycle.shadow_model.structural_eligibility import (
    evaluate_structural_eligibility,
)


def test_structural_eligibility_does_not_select_candidate_phase() -> None:
    summary = evaluate_structural_eligibility([])

    assert summary["structural_candidate_eligibility_ready"] is True
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_computed"] is False
    assert summary["candidate_phase"] is None
    assert summary["aggregation_eligible_phase_count"] == 0
