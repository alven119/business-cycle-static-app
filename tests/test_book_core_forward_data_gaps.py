from __future__ import annotations

from business_cycle.audits.book_core_forward_data_gaps import (
    summarize_book_core_forward_data_gaps,
)


def test_book_core_forward_data_gap_registry_covers_40_roles() -> None:
    summary = summarize_book_core_forward_data_gaps()

    assert summary["forward_data_gap_registry_ready"] is True
    assert summary["role_count"] == 40
    assert summary["role_without_forward_status_count"] == 0
    assert summary["forward_ready_misclassified_historical_ready_count"] == 0
    assert summary["silent_forward_substitution_count"] == 0
    assert summary["historical_strict_partial_role_count"] > 0
    assert summary["forward_capture_ready_role_count"] == 35
    assert summary["forward_blocked_role_count"] == 5
    assert summary["forward_source_identity_blocked_role_count"] == 0
