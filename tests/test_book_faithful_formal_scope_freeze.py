from __future__ import annotations

from business_cycle.audits.formal_scope_freeze import (
    summarize_book_faithful_formal_scope_freeze,
)


def test_scope_freeze_hashes_are_reproducible() -> None:
    summary = summarize_book_faithful_formal_scope_freeze()

    assert summary["formal_scope_freeze_ready"] is True
    assert summary["scope_freeze_hash_valid"] is True
    assert summary["scope_freeze_missing_file_count"] == 0
    assert summary["scope_freeze_hash_mismatch_count"] == 0
    assert summary["scope_freeze_secret_count"] == 0
    assert summary["decision_parameter_frozen_by_scope_phase_count"] == 0
    assert summary["implementation_status"] == "scope_defined_not_implemented"
    assert summary["holdout_status"] == "not_registered_for_candidate_model"

