from __future__ import annotations

from business_cycle.audits.phase10_book_core_source_adapter_closure import (
    summarize_phase10_book_core_source_adapter_closure,
)


def test_phase10_observation_runtime_stays_observation_only() -> None:
    summary = summarize_phase10_book_core_source_adapter_closure()

    assert summary["new_runtime_observable_role_count"] == 11
    assert summary["new_phase_evidence_evaluable_role_count"] == 0
    assert summary["new_candidate_selection_eligible_role_count"] == 0
    assert summary["new_numeric_threshold_count"] == 0
    assert summary["new_weight_count"] == 0
    assert summary["formal_candidate_phase_computed"] is False
