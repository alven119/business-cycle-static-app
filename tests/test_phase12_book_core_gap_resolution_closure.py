from __future__ import annotations

from business_cycle.audits.phase12_book_core_gap_resolution_closure import (
    summarize_phase12_book_core_gap_resolution_closure,
)


def test_phase12_book_core_gap_resolution_closure_passes() -> None:
    summary = summarize_phase12_book_core_gap_resolution_closure()

    assert summary["result"] == "passed"
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["gap_resolution_registry_ready"] is True
    assert summary["remaining_gap_reviewed_count"] == 9
    assert summary["false_resolution_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_registry_record_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["alpha8_freeze_hash_valid"] is True
    assert summary["alpha7_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["candidate_capability_ready"] is False
    assert summary["formal_decision_model_ready"] is False
    assert summary["economic_validation_status"] == "not_started"
    assert summary["book_alignment_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
    assert summary["development_next_phase"] == 13
    assert summary["prospective_track_next_action"] == "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
    assert summary["phase12_closure_status"] == (
        "closed_remaining_book_core_gaps_reviewed_no_false_resolution_alpha8_"
        "frozen_candidate_model_disabled"
    )


def test_phase12_final_report_north_star_fields_are_present() -> None:
    summary = summarize_phase12_book_core_gap_resolution_closure()

    assert summary["phase_id"] == 12
    assert summary["product_capabilities_advanced"]
    assert summary["web_surfaces_advanced"]
    assert summary["deferred_capability_gaps"]
    assert summary["production_behavior_change_count"] == 0
