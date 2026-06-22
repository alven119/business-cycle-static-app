from __future__ import annotations

from business_cycle.audits.qa10_shadow_runtime_monitoring_readiness_closure import (
    summarize_qa10_shadow_runtime_monitoring_readiness_closure,
)


def test_qa10_shadow_runtime_monitoring_readiness_closure_passes() -> None:
    summary = summarize_qa10_shadow_runtime_monitoring_readiness_closure()

    assert summary["result"] == "passed"
    assert summary["qa8_qa9_lineage_verified"] is True
    assert summary["implemented_evaluator_runtime_path_ready"] is True
    assert summary["runtime_output_on_2019_revised_count"] == 1
    assert summary["real_registry_record_count"] == 0
    assert summary["candidate_capability_ready"] is False
    assert summary["prospective_protocol_started"] is False
    assert summary["holdout_registered"] is False
    assert summary["recommended_next_phase"] == "QA11"
    assert (
        summary["qa10_closure_status"]
        == "closed_runtime_path_ready_prestart_no_real_records_candidate_capability_incomplete"
    )
