from __future__ import annotations

from business_cycle.audits.book_faithful_scope import summarize_recovery_formal_scope


def test_recovery_scope_keeps_core_roles_separate() -> None:
    summary = summarize_recovery_formal_scope()

    assert summary["recovery_scope_ready"] is True
    assert summary["recovery_book_core_role_count"] == 10
    assert summary["recovery_formal_v1_ready_count"] == 3
    assert summary["recovery_experimental_ready_count"] >= 6
    assert summary["recovery_modern_substitute_count"] == 0
    assert summary["recovery_minimum_scope_ready"] is False

