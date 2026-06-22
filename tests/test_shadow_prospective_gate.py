from __future__ import annotations

from business_cycle.shadow_model.prospective_gate import (
    evaluate_prospective_shadow_gate,
    summarize_prospective_gate_fixtures,
)


def test_prospective_gate_blocks_pre_start_backfill_and_mismatch() -> None:
    assert evaluate_prospective_shadow_gate(
        as_of="2026-07-15",
        rule_version="book_faithful_shadow_v2_alpha4",
        period_complete=True,
        evidence_complete=True,
    )["status"] == "rejected_pre_start"
    assert evaluate_prospective_shadow_gate(
        as_of="2026-08-31",
        rule_version="book_faithful_shadow_v2_alpha4",
        period_complete=True,
        evidence_complete=True,
        rerun_requested_at="2026-07-01",
    )["status"] == "rejected_backfill"
    assert evaluate_prospective_shadow_gate(
        as_of="2026-08-31",
        rule_version="book_faithful_shadow_v2_alpha5",
        period_complete=True,
        evidence_complete=True,
    )["status"] == "rejected_rule_version_mismatch"


def test_prospective_gate_allows_only_shadow_diagnostic_when_complete() -> None:
    result = evaluate_prospective_shadow_gate(
        as_of="2026-08-31",
        rule_version="book_faithful_shadow_v2_alpha4",
        period_complete=True,
        evidence_complete=True,
    )

    assert result["status"] == "eligible_shadow_diagnostic"
    assert result["production_integration"] is False
    assert result["holdout"] is False
    assert result["performance_claim"] is False
    assert result["portfolio_output"] is False


def test_prospective_gate_hard_gate_counts_are_zero() -> None:
    summary = summarize_prospective_gate_fixtures()

    assert summary["prospective_clock_gate_ready"] is True
    assert summary["pre_start_selection_count"] == 0
    assert summary["backfill_selection_count"] == 0
    assert summary["incomplete_period_selection_count"] == 0
    assert summary["incomplete_evidence_selection_count"] == 0
    assert summary["rule_version_mismatch_accepted_count"] == 0
    assert summary["context_injection_accepted_count"] == 0
