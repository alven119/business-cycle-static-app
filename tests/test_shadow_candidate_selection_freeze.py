from __future__ import annotations

from business_cycle.audits.shadow_candidate_selection_freeze import (
    summarize_shadow_candidate_selection_freeze,
)


def test_shadow_candidate_selection_freeze_is_reproducible() -> None:
    summary = summarize_shadow_candidate_selection_freeze()

    assert summary["candidate_selection_freeze_ready"] is True
    assert summary["freeze_hash_valid"] is True
    assert summary["freeze_missing_file_count"] == 0
    assert summary["freeze_hash_mismatch_count"] == 0
    assert summary["parent_freeze_missing_count"] == 0
    assert summary["secret_in_freeze_count"] == 0
    assert summary["production_file_in_freeze_count"] == 0
    assert summary["numeric_weight_frozen_count"] == 0
    assert summary["production_threshold_change_count"] == 0
    assert summary["holdout_registered"] is False
