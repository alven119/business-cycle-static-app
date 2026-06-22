from __future__ import annotations

from datetime import date

from business_cycle.shadow_model.prospective_forward_gate import (
    ForwardGateRequest,
    evaluate_forward_gate,
    summarize_forward_clock_gate,
)


def test_forward_clock_gate_rejects_pre_start() -> None:
    result = evaluate_forward_gate(
        ForwardGateRequest(
            clock_date=date(2026, 6, 22),
            dry_run=True,
            metadata_only=True,
            no_write=True,
        )
    )

    assert result["gate_status"] == "rejected_pre_start"
    assert result["record_written"] is False
    assert result["candidate_phase_emitted"] is False


def test_forward_clock_gate_rejects_arbitrary_real_as_of_override() -> None:
    result = evaluate_forward_gate(
        ForwardGateRequest(
            clock_date=date(2026, 9, 1),
            requested_as_of="2008-09-30",
            dry_run=True,
            metadata_only=True,
            no_write=True,
        )
    )

    assert result["gate_status"] == "rejected_noncanonical_as_of"
    assert result["arbitrary_real_as_of_override_count"] == 1


def test_forward_clock_gate_summary_keeps_candidate_disabled() -> None:
    summary = summarize_forward_clock_gate()

    assert summary["forward_clock_gate_ready"] is True
    assert summary["candidate_capability_ready"] is False
    assert summary["candidate_monitoring_allowed"] is False
    assert summary["candidate_emission_without_capability_count"] == 0
