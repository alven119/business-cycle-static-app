from __future__ import annotations

from business_cycle.audits.book_faithful_scope import (
    summarize_recession_trough_formal_scope,
)


def test_recession_confirmation_and_trough_are_separate() -> None:
    summary = summarize_recession_trough_formal_scope()

    assert summary["recession_trough_scope_ready"] is True
    assert summary["recession_confirmation_core_role_count"] == 5
    assert summary["recession_trough_core_role_count"] == 4
    assert summary["recovery_watch_supporting_role_count"] == 1
    assert summary["formal_v1_ready_count"] == 1
    assert summary["experimental_ready_count"] == 8
    assert summary["minimum_scope_ready"] is False

