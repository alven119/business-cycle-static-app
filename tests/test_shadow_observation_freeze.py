from __future__ import annotations

from business_cycle.audits.shadow_observation_freeze import (
    summarize_shadow_observation_freeze,
)


def test_shadow_observation_freeze_is_valid_alpha5_lineage() -> None:
    summary = summarize_shadow_observation_freeze()

    assert summary["observation_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha5"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha4"
    assert summary["freeze_hash_valid"] is True
    assert summary["parent_freeze_present"] is True
    assert summary["prior_freeze_preserved"] is True
    assert summary["missing_file_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["holdout_registered"] is False

