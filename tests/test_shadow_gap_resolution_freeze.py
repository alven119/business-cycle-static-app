from __future__ import annotations

from business_cycle.audits.shadow_gap_resolution_freeze import (
    summarize_shadow_gap_resolution_freeze,
)


def test_alpha8_gap_resolution_freeze_is_valid() -> None:
    summary = summarize_shadow_gap_resolution_freeze()

    assert summary["gap_resolution_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha8"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha7"
    assert summary["alpha8_freeze_hash_valid"] is True
    assert summary["alpha7_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["candidate_selection_enabled"] is False
    assert summary["current_phase_enabled"] is False
    assert summary["prospective_protocol_started"] is False
    assert summary["prospective_registry_record_count"] == 0
    assert summary["holdout_registered"] is False


def test_alpha8_freeze_records_gap_registry_without_rewriting_parent() -> None:
    summary = summarize_shadow_gap_resolution_freeze()

    assert summary["gap_resolution_registry_ready"] is True
    assert summary["newly_operationalized_evaluator_count"] == 0
    assert summary["false_resolution_count"] == 0
    assert summary["parent_freeze"]["freeze_id"] == "book_faithful_shadow_v2_alpha7"
    assert summary["parent_freeze"]["phase_evidence_freeze_ready"] is True
