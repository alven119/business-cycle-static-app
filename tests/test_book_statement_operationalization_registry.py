from __future__ import annotations

from business_cycle.audits.book_statement_operationalization import (
    statement_by_id,
    summarize_book_statement_operationalization_registry,
)


def test_book_statement_operationalization_hard_gates() -> None:
    summary = summarize_book_statement_operationalization_registry()

    assert summary["book_statement_operationalization_ready"] is True
    assert summary["contextual_example_used_as_universal_rule_count"] == 0
    assert summary["qualitative_statement_given_arbitrary_threshold_count"] == 0
    assert summary["statement_without_source_provenance_count"] == 0


def test_250k_claims_example_is_contextual_not_universal() -> None:
    row = statement_by_id("claims_2019_250k_contextual_example")

    assert row["classification"] == "book_contextual_historical_example"
    assert row["universal_across_cycles"] is False
    assert row["can_be_used_as_shadow_rule"] is False


def test_three_month_moving_average_is_book_smoothing_rule() -> None:
    row = statement_by_id("claims_3_month_moving_average_noise_filter")

    assert row["classification"] == "book_explicit_smoothing_rule"
    assert row["smoothing_period"] == "3_months"
    assert row["prohibited_generalization_reason"] == "not_phase_confirmation_by_itself"
