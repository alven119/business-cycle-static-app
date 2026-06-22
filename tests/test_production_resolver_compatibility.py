from __future__ import annotations

from business_cycle.audits.qa2_context_ablation_closure import (
    summarize_production_compatibility,
)


def test_production_resolver_golden_fixtures_are_preserved() -> None:
    summary = summarize_production_compatibility()

    assert summary["production_golden_case_count"] > 0
    assert summary["production_golden_match_count"] == summary["production_golden_case_count"]
    assert summary["production_golden_mismatch_count"] == 0
    assert summary["production_default_behavior_changed_count"] == 0
