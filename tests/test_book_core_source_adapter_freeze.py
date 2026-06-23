from __future__ import annotations

from business_cycle.audits.book_core_source_adapter_freeze import (
    summarize_book_core_source_adapter_freeze,
)


def test_phase10_source_adapter_freeze_is_valid_alpha6_lineage() -> None:
    summary = summarize_book_core_source_adapter_freeze()

    assert summary["source_adapter_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha6"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha5"
    assert summary["freeze_hash_valid"] is True
    assert summary["parent_freeze_present"] is True
    assert summary["prior_freeze_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["candidate_selection_enabled"] is False
    assert summary["holdout_registered"] is False
