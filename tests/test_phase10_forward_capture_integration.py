from __future__ import annotations

from business_cycle.audits.book_core_forward_data_gaps import (
    summarize_book_core_forward_data_gaps,
)
from business_cycle.audits.phase10_common import before_forward_rows, ready_role_ids


def test_phase10_forward_capture_expands_ready_roles_without_deleting_scope() -> None:
    summary = summarize_book_core_forward_data_gaps()

    assert len(before_forward_rows()) == 40
    assert summary["role_count"] == 40
    assert summary["forward_capture_ready_role_count"] == 35
    assert len(ready_role_ids(before_forward_rows())) == 24
    assert summary["forward_blocked_role_count"] == 5
    assert summary["forward_source_identity_blocked_role_count"] == 0
    assert summary["silent_forward_substitution_count"] == 0
