from __future__ import annotations

from business_cycle.audits.formal_scope_diff import summarize_formal_model_scope_diff


def test_formal_scope_diff_has_no_current_behavior_change() -> None:
    summary = summarize_formal_model_scope_diff()

    assert summary["formal_scope_diff_ready"] is True
    assert summary["current_formal_v1_indicator_count"] == 13
    assert summary["proposed_v2_core_role_count"] == 77
    assert summary["proposed_v2_missing_role_count"] == 16
    assert summary["production_behavior_change_count"] == 0
    assert all(row["decision_behavior_changed_now"] is False for row in summary["rows"])

