from __future__ import annotations

from business_cycle.audits.indicator_promotion import (
    summarize_indicator_promotion_readiness,
)


def test_indicator_promotion_gate_blocks_unready_candidates() -> None:
    summary = summarize_indicator_promotion_readiness()

    assert summary["indicator_promotion_gate_ready"] is True
    assert summary["promotion_candidate_count"] > 0
    assert summary["production_review_ready_count"] == 0
    assert summary["promotion_without_complete_gate_count"] == 0
    assert summary["contaminated_indicator_promoted_without_disclosure_count"] == 0
    assert summary["silent_substitution_promotion_count"] == 0
    assert summary["new_production_promotion_count"] == 0

