from __future__ import annotations

from business_cycle.audits.shadow_evaluator_freeze import (
    summarize_shadow_evaluator_freeze,
)


def test_shadow_evaluator_freeze_is_reproducible() -> None:
    summary = summarize_shadow_evaluator_freeze()

    assert summary["evaluator_freeze_ready"] is True
    assert summary["freeze_hash_valid"] is True
    assert summary["parent_freeze_present"] is True
    assert summary["prior_freeze_preserved"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["non_book_threshold_added_count"] == 0
    assert summary["holdout_registered"] is False
