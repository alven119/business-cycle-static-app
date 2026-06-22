from __future__ import annotations

from business_cycle.audits.qa11_book_core_evaluator_data_gap_closure import (
    summarize_qa11_book_core_evaluator_data_gap_closure,
)


def test_qa11_book_core_evaluator_data_gap_closure_passes() -> None:
    summary = summarize_qa11_book_core_evaluator_data_gap_closure()

    assert summary["result"] == "passed"
    assert summary["forward_data_gap_registry_ready"] is True
    assert summary["runtime_observable_role_count"] > 1
    assert summary["candidate_capability_ready"] is False
    assert summary["candidate_monitoring_allowed"] is False
    assert summary["real_registry_record_count"] == 0
    assert summary["prospective_protocol_started"] is False
    assert summary["holdout_registered"] is False
    assert summary["recommended_next_phase"] == "QA12"
    assert (
        summary["qa11_closure_status"]
        == "closed_forward_observation_runtime_expanded_candidate_capability_incomplete"
    )

