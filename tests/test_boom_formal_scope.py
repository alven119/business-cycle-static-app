from __future__ import annotations

from business_cycle.audits.book_faithful_scope import summarize_boom_formal_scope


def test_boom_scope_preserves_missing_book_roles() -> None:
    summary = summarize_boom_formal_scope()

    assert summary["boom_scope_ready"] is True
    assert summary["boom_book_core_role_count"] == 11
    assert summary["boom_formal_v1_ready_count"] == 1
    assert summary["boom_missing_count"] == 10
    assert summary["boom_minimum_scope_ready"] is False

