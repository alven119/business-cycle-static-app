from __future__ import annotations

from business_cycle.audits.phase10_book_core_source_adapter_closure import (
    summarize_phase10_book_core_source_adapter_closure,
)


def test_phase10_book_core_source_adapter_closure_passes_with_blockers() -> None:
    summary = summarize_phase10_book_core_source_adapter_closure()

    assert summary["result"] == "passed"
    assert summary["blocked_role_inventory_reconciled"] is True
    assert summary["source_identity_contract_ready"] is True
    assert summary["all_safely_implementable_adapters_completed"] is True
    assert summary["new_adapter_implemented_count"] == 11
    assert summary["new_forward_capture_ready_role_count"] == 11
    assert summary["genuine_blocker_count_after"] == 5
    assert summary["candidate_capability_ready"] is False
    assert summary["candidate_monitoring_allowed"] is False
    assert summary["prospective_protocol_started"] is False
    assert summary["real_registry_record_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["development_next_phase"] == 11
    assert summary["prospective_track_next_action"] == "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
    assert (
        summary["phase10_closure_status"]
        == "closed_source_identity_resolved_adapters_expanded_with_explicit_blockers"
    )
