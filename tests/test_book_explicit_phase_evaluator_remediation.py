from __future__ import annotations

from business_cycle.audits.book_explicit_phase_evaluator_remediation import (
    summarize_book_explicit_phase_evaluator_remediation,
)


def test_phase_evaluator_remediation_does_not_add_arbitrary_rules() -> None:
    summary = summarize_book_explicit_phase_evaluator_remediation()

    assert summary["book_explicit_evaluator_remediation_ready"] is True
    assert summary["operational_rule_silently_skipped_count"] == 0
    assert summary["incomplete_rule_implemented_count"] == 0
    assert summary["historical_result_used_to_complete_rule_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["arbitrary_persistence_added_count"] == 0

