from __future__ import annotations

from datetime import date

from business_cycle.audits.prospective_wait_state import (
    summarize_prospective_wait_state,
)


def test_wait_state_blocks_next_phase_and_real_append_before_asof() -> None:
    summary = summarize_prospective_wait_state(clock=date(2026, 6, 23))

    assert summary["wait_state_governance_ready"] is True
    assert summary["current_wait_state"] == "pre_period"
    assert summary["next_check_date"] == "2026-08-31"
    assert summary["earliest_possible_manual_append_at"] == "2026-10-31"
    assert summary["qa13_allowed_now"] is False
    assert summary["qa13_earliest_as_of"] == "2026-08-31"
    assert summary["real_registry_append_allowed_now"] is False
    assert summary["candidate_monitoring_allowed_now"] is False
