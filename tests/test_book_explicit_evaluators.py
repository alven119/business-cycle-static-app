from __future__ import annotations

from business_cycle.shadow_model.evidence_evaluators import (
    evaluate_book_explicit_rule,
    summarize_book_explicit_evaluators,
)


def test_claims_three_month_ma_is_noise_filter_only() -> None:
    result = evaluate_book_explicit_rule(
        role_id="recovery_weekly_claim_noise_filter",
        observations=[
            {"date": "2026-01-07", "value": 220000},
            {"date": "2026-02-04", "value": 210000},
            {"date": "2026-03-04", "value": 200000},
        ],
        as_of="2026-03-31",
        data_mode="vintage_as_of",
    )

    assert result["rule_match_status"] == "matched"
    assert result["typed_evidence_state"] == "noise_filter_observation"
    assert result["candidate_selection_eligible"] is False
    assert result["contextual_example_used"] is False
    assert result["historical_label_used"] is False


def test_incomplete_rules_abstain_without_directional_evidence() -> None:
    result = evaluate_book_explicit_rule(
        role_id="trough_claims_reversal",
        observations=[
            {"date": "2026-01-01", "value": 1},
            {"date": "2026-02-01", "value": 0},
        ],
        as_of="2026-02-28",
        data_mode="vintage_as_of",
    )

    assert result["rule_match_status"] == "abstained"
    assert result["typed_evidence_state"] == "unresolved_rule_abstention"
    assert result["candidate_selection_eligible"] is False


def test_evaluator_misclassification_counts_are_zero() -> None:
    summary = summarize_book_explicit_evaluators()

    assert summary["book_explicit_evaluators_implemented"] is True
    assert summary["implemented_explicit_evaluator_count"] == 1
    assert summary["evaluator_candidate_selection_eligible_count"] == 0
    assert summary["smoothing_misclassified_as_directional_count"] == 0
    assert summary["directional_misclassified_as_confirmation_count"] == 0
    assert summary["unresolved_rule_emitted_directional_evidence_count"] == 0
