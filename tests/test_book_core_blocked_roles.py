from __future__ import annotations

from business_cycle.audits.book_core_blocked_roles import (
    build_book_core_blocked_role_inventory_rows,
    summarize_book_core_blocked_roles,
)


def test_book_core_blocked_roles_are_reconciled_from_canonical_contracts() -> None:
    summary = summarize_book_core_blocked_roles()
    rows = build_book_core_blocked_role_inventory_rows()

    assert summary["blocked_role_inventory_reconciled"] is True
    assert summary["blocked_role_count_before"] == 16
    assert summary["blocked_role_count_after"] == 5
    assert summary["source_identity_unknown_count_before"] == 13
    assert summary["role_without_blocker_evidence_count"] == 0
    assert summary["duplicate_blocked_role_count"] == 0
    assert summary["blocked_role_not_in_canonical_scope_count"] == 0
    assert len({row["role_id"] for row in rows}) == 16
    assert {row["current_blocker_class"] for row in rows} <= {
        "source_identity_unknown",
        "proprietary_access_required",
        "official_source_found_release_semantics_missing",
    }
