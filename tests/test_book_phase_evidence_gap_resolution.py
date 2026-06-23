from __future__ import annotations

from business_cycle.audits.book_phase_evidence_gap_resolution import (
    REMAINING_PHASE11_GAP_IDS,
    summarize_book_phase_evidence_gap_resolution,
)


def test_phase12_reviews_all_remaining_gaps_without_false_resolution() -> None:
    summary = summarize_book_phase_evidence_gap_resolution()

    assert summary["gap_resolution_registry_ready"] is True
    assert summary["remaining_gap_reviewed_count"] == 9
    assert summary["remaining_gap_reviewed_count"] == len(REMAINING_PHASE11_GAP_IDS)
    assert summary["missing_expected_gap_count"] == 0
    assert summary["unexpected_gap_count"] == 0
    assert summary["duplicate_gap_count"] == 0
    assert summary["phase11_gap_status_mismatch_count"] == 0
    assert summary["false_resolution_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["historical_tuning_leakage_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_phase12_blocks_silent_substitutions_and_noise_filter_support() -> None:
    summary = summarize_book_phase_evidence_gap_resolution()
    rows = {row["role_id"]: row for row in summary["rows"]}

    assert rows["growth_adp_employment"]["blocker_class"] == (
        "proprietary_access_required"
    )
    assert "PAYEMS" in rows["growth_adp_employment"]["prohibited_substitutions"]
    assert rows["boom_consumer_confidence"]["blocker_class"] == (
        "no_public_official_equivalent"
    )
    assert rows["growth_core_cpi"]["phase_support_added"] is False
    assert rows["growth_core_pce"]["phase_support_added"] is False
    assert rows["recovery_weekly_claim_noise_filter"]["blocker_class"] == (
        "smoothing_not_phase_evidence"
    )
    assert rows["recovery_weekly_claim_noise_filter"][
        "operational_evaluator_added"
    ] is False
    assert rows["trough_policy_financial_not_sufficient_alone"][
        "resolution_status"
    ] == "retained_supporting_only"


def test_phase12_has_no_new_operational_evaluator_or_candidate_input() -> None:
    summary = summarize_book_phase_evidence_gap_resolution()

    assert summary["safe_to_operationalize_count"] == 0
    assert summary["newly_operationalized_evaluator_count"] == 0
    assert summary["phase_support_added_count"] == 0
    assert summary["candidate_selection_eligible_count"] == 0
    assert summary["prohibited_substitution_count"] == 0
