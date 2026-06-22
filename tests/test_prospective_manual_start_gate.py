from __future__ import annotations

from datetime import date

from business_cycle.shadow_model.manual_start_gate import summarize_manual_start_gate


def test_manual_start_gate_requires_canonical_asof_and_complete_period() -> None:
    summary = summarize_manual_start_gate(clock=date(2026, 6, 23))

    assert summary["manual_start_gate_ready"] is True
    assert summary["canonical_as_of"] == "2026-08-31"
    assert summary["canonical_as_of_reached"] is False
    assert summary["period_complete"] is False
    assert summary["manual_start_contract_ready"] is True
    assert summary["manual_start_allowed_now"] is False
    assert summary["real_append_allowed_now"] is False
    assert summary["candidate_monitoring_allowed"] is False
    assert summary["explicit_user_command_required"] is True
    assert summary["force_clock_bypass_option_count"] == 0
    assert summary["automatic_start_path_count"] == 0
    assert summary["start_before_canonical_as_of_count"] == 0
    assert summary["start_with_incomplete_period_count"] == 0
    assert summary["start_without_explicit_user_command_count"] == 0

