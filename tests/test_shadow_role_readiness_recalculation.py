from __future__ import annotations

from business_cycle.audits.evidence_evaluability import (
    summarize_shadow_role_readiness_recalculation,
)


def test_shadow_role_readiness_recalculation_promotes_only_fully_gated_role() -> None:
    summary = summarize_shadow_role_readiness_recalculation()

    assert summary["role_readiness_recalculated"] is True
    assert summary["implemented_evaluator_role_count"] == 1
    assert summary["evidence_evaluable_role_count"] == 1
    assert summary["candidate_selection_eligible_role_count"] == 0
    assert summary["fully_gated_role_still_not_evaluable_count"] == 0
    assert summary["incompletely_gated_role_marked_evaluable_count"] == 0
