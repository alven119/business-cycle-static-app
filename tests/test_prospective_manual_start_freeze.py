from __future__ import annotations

from business_cycle.audits.prospective_manual_start_freeze import (
    summarize_prospective_manual_start_freeze,
)


def test_manual_start_freeze_hash_and_lineage_are_valid() -> None:
    summary = summarize_prospective_manual_start_freeze()

    assert summary["manual_start_freeze_ready"] is True
    assert summary["freeze_id"] == "prospective_shadow_manual_start_v1"
    assert summary["parent_model_freeze_id"] == "book_faithful_shadow_v2_alpha5"
    assert summary["parent_monitoring_freeze_id"] == "prospective_shadow_monitoring_v1"
    assert summary["freeze_hash_valid"] is True
    assert summary["parent_model_freeze_present"] is True
    assert summary["parent_monitoring_freeze_present"] is True
    assert summary["prior_freezes_preserved"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["holdout_registered"] is False

