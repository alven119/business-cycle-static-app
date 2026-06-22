from __future__ import annotations

from business_cycle.indicators.strict_scoring_policy import (
    load_strict_scoring_abstention_policy,
    strict_scoring_summary,
)


def test_strict_scoring_abstention_never_zero_fills_or_fallbacks() -> None:
    policy = load_strict_scoring_abstention_policy()
    summary = strict_scoring_summary(
        total_count=13,
        scored_count=9,
        missing_temporal_dependencies=["ICSA", "DGS10"],
    )

    assert policy["statuses"]["abstained_missing_temporal_evidence"]["zero_fill_allowed"] is False
    assert summary["temporal_abstention_count"] == 2
    assert summary["temporal_abstention_zero_fill_count"] == 0
    assert summary["complete_phase_score_allowed"] is False
    assert summary["incomplete_score_sent_to_formal_resolver_count"] == 0
    assert summary["strict_fallback_count"] == 0
