from __future__ import annotations

from business_cycle.audits.book_core_release_semantics import (
    summarize_book_core_release_semantics,
)


def test_book_core_release_semantics_are_explicit_for_all_roles() -> None:
    summary = summarize_book_core_release_semantics()

    assert summary["release_semantics_registry_ready"] is True
    assert summary["role_with_release_semantics_count"] == 40
    assert summary["role_without_release_semantics_count"] == 0
    assert summary["direct_role_without_revision_policy_count"] == 0
    assert summary["derived_role_without_input_semantics_count"] == 0
    assert summary["ambiguous_availability_date_count"] == 0
    assert summary["observation_date_assumed_availability_count"] == 0
