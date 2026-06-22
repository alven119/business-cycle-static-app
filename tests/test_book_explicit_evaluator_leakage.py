from __future__ import annotations

from business_cycle.audits.book_explicit_evaluator_leakage import (
    summarize_book_explicit_evaluator_leakage,
)


def test_book_explicit_evaluator_leakage_counts_are_zero() -> None:
    summary = summarize_book_explicit_evaluator_leakage()

    assert summary["evaluator_leakage_guard_ready"] is True
    assert summary["scenario_id_reference_count"] == 0
    assert summary["historical_date_reference_count"] == 0
    assert summary["expected_label_reference_count"] == 0
    assert summary["nber_reference_count"] == 0
    assert summary["return_metric_reference_count"] == 0
    assert summary["copied_historical_threshold_count"] == 0
    assert summary["contextual_250k_executable_count"] == 0
    assert summary["post_diagnostic_rule_change_without_new_version_count"] == 0
