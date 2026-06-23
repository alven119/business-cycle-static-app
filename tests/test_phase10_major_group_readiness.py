from __future__ import annotations

from business_cycle.audits.phase10_book_core_source_adapter_closure import (
    summarize_phase10_book_core_source_adapter_closure,
)


def test_phase10_major_group_readiness_recalculates_without_shortcuts() -> None:
    summary = summarize_phase10_book_core_source_adapter_closure()

    assert summary["major_group_readiness_recalculated"] is True
    assert summary["observation_contract_ready_group_count"] == 19
    assert summary["phase_evidence_ready_group_count"] == 0
    assert summary["candidate_input_complete_group_count"] == 0
    assert summary["group_promoted_with_missing_core_role_count"] == 0
    assert summary["group_promoted_via_modern_extension_count"] == 0
    assert summary["readiness_semantics_violation_count"] == 0
