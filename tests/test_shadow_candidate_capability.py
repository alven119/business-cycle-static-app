from __future__ import annotations

from business_cycle.audits.shadow_candidate_capability import (
    summarize_shadow_candidate_capability,
)


def test_shadow_candidate_capability_remains_disabled() -> None:
    summary = summarize_shadow_candidate_capability()

    assert summary["evaluator_runtime_ready"] is True
    assert summary["evidence_monitoring_ready"] is True
    assert summary["major_group_evidence_ready"] is False
    assert summary["candidate_selection_contract_ready"] is True
    assert summary["candidate_selection_input_complete"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["candidate_monitoring_allowed"] is False
    assert summary["capability_promoted_by_single_evaluator_count"] == 0
    assert summary["candidate_phase_emitted_without_capability_count"] == 0
