from __future__ import annotations

from business_cycle.audits.book_faithful_scope import summarize_growth_formal_scope


def test_growth_scope_preserves_missing_book_roles() -> None:
    summary = summarize_growth_formal_scope()

    assert summary["growth_scope_ready"] is True
    assert summary["growth_book_core_role_count"] == 10
    assert summary["growth_formal_v1_ready_count"] == 1
    assert summary["growth_missing_count"] == 9
    assert summary["growth_data_contract_blocked_count"] == 1
    assert summary["growth_minimum_scope_ready"] is False

