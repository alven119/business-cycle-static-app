from __future__ import annotations

from datetime import date

from business_cycle.shadow_model.period_completeness import (
    evaluate_period_completeness,
)


def test_period_completeness_pre_start_does_not_complete_groups() -> None:
    summary = evaluate_period_completeness(clock=date(2026, 6, 23))

    assert summary["period_completeness_engine_ready"] is True
    assert summary["global_status"] == "pre_start"
    assert summary["period_complete_group_count"] == 0
    assert summary["phase_evidence_ready_group_count"] == 0
    assert summary["candidate_input_complete_group_count"] == 0
    assert summary["incomplete_group_marked_complete_count"] == 0
    assert summary["missing_core_role_ignored_count"] == 0
    assert summary["supporting_role_substitution_count"] == 0
    assert summary["late_release_silently_ignored_count"] == 0

