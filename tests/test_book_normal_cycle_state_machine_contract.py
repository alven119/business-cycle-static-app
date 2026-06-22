from __future__ import annotations

from business_cycle.audits.qa4_scope_contracts import (
    summarize_book_normal_cycle_state_machine_contract,
)


def test_normal_cycle_contract_excludes_duration_and_context_shortcuts() -> None:
    summary = summarize_book_normal_cycle_state_machine_contract()

    assert summary["normal_cycle_contract_ready"] is True
    assert summary["phase_duration_hardcoded_count"] == 0
    assert summary["boom_year_schedule_used_as_phase_transition_count"] == 0
    assert summary["external_context_in_normal_state_machine_count"] == 0
    assert summary["display_hint_in_normal_state_machine_count"] == 0
    assert summary["normal_sequence_violation_count"] == 0

