from __future__ import annotations

from business_cycle.audits.formal_phase_decision_eligibility import (
    summarize_formal_phase_decision_eligibility,
)


def test_incomplete_strict_scores_do_not_reach_formal_decision_or_resolver() -> None:
    summary = summarize_formal_phase_decision_eligibility()

    assert summary["formal_phase_decision_pair_count"] == 252
    assert summary["incomplete_strict_phase_decision_count"] == 0
    assert summary["incomplete_strict_resolver_input_count"] == 0
    assert summary["partial_score_without_diagnostic_label_count"] == 0
    assert summary["diagnostic_partial_phase_score_pair_count"] > 0
