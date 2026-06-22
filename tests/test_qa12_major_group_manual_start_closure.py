from __future__ import annotations

from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)


def test_qa12_major_group_manual_start_closure_passes() -> None:
    summary = summarize_qa12_major_group_manual_start_closure()

    assert summary["result"] == "passed"
    assert summary["readiness_semantics_reconciled"] is True
    assert summary["capture_topology_valid"] is True
    assert summary["no_write_source_preflight_ready"] is True
    assert summary["first_period_manifest_ready"] is True
    assert summary["manual_start_freeze_ready"] is True
    assert summary["period_complete_group_count"] == 0
    assert summary["phase_evidence_ready_group_count"] == 0
    assert summary["candidate_input_complete_group_count"] == 0
    assert summary["manual_start_contract_ready"] is True
    assert summary["manual_start_allowed_now"] is False
    assert summary["real_append_allowed_now"] is False
    assert summary["real_registry_record_count"] == 0
    assert summary["prospective_protocol_started"] is False
    assert summary["candidate_capability_ready"] is False
    assert summary["qa13_allowed_now"] is False
    assert summary["qa13_earliest_as_of"] == "2026-08-31"
    assert summary["recommended_next_action"] == "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
    assert (
        summary["qa12_closure_status"]
        == "closed_manual_start_contract_ready_waiting_first_eligible_asof"
    )

