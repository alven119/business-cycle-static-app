from __future__ import annotations

from business_cycle.audits.qa6_shadow_aggregation_closure import (
    summarize_qa6_shadow_aggregation_closure,
)


def test_qa6_shadow_aggregation_closure_passes_with_selection_disabled() -> None:
    summary = summarize_qa6_shadow_aggregation_closure()

    assert summary["result"] == "passed"
    assert summary["freeze_lineage_ready"] is True
    assert summary["aggregation_schema_preregistered"] is True
    assert summary["synthetic_structural_eligibility_validated"] is True
    assert summary["candidate_selection_enabled"] is False
    assert summary["formal_candidate_phase_computed"] is False
    assert summary["holdout_registered"] is False
    assert summary["qa7_allowed"] is True
    assert summary["recommended_next_phase"] == "QA7"
    assert (
        summary["qa6_closure_status"]
        == "closed_aggregation_schema_preregistered_candidate_selection_disabled"
    )
