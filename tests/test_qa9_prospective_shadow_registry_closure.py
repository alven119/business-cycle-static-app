from __future__ import annotations

from business_cycle.audits.qa9_prospective_shadow_registry_closure import (
    summarize_qa9_prospective_shadow_registry_closure,
)


def test_qa9_prospective_shadow_registry_closure_passes() -> None:
    summary = summarize_qa9_prospective_shadow_registry_closure()

    assert summary["result"] == "passed"
    assert summary["evaluator_runtime_audit_ready"] is True
    assert summary["implemented_evaluator_runtime_wired"] is True
    assert summary["registry_contract_ready"] is True
    assert summary["append_only_store_ready"] is True
    assert summary["forward_clock_gate_ready"] is True
    assert summary["monitoring_infrastructure_freeze_ready"] is True
    assert summary["production_isolation_verified"] is True
    assert summary["protocol_started"] is False
    assert summary["real_record_count"] == 0
    assert summary["candidate_capability_ready"] is False
    assert summary["holdout_registered"] is False
    assert summary["recommended_next_phase"] == "QA10"
    assert (
        summary["qa9_closure_status"]
        == "closed_forward_registry_armed_not_started_candidate_capability_incomplete"
    )
