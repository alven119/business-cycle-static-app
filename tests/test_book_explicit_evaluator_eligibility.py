from __future__ import annotations

from business_cycle.audits.book_explicit_evaluator_eligibility import (
    summarize_book_explicit_evaluator_eligibility,
)


def test_only_operationally_complete_explicit_rules_are_implemented() -> None:
    summary = summarize_book_explicit_evaluator_eligibility()

    assert summary["explicit_rule_eligibility_ready"] is True
    assert summary["operationally_complete_explicit_rule_count"] == 1
    assert summary["implementation_required_rule_count"] == 1
    assert summary["implemented_explicit_evaluator_count"] == 1
    assert summary["explicit_rule_silently_skipped_count"] == 0
    assert summary["ineligible_rule_implemented_count"] == 0


def test_incomplete_explicit_rules_remain_blocked() -> None:
    rows = summarize_book_explicit_evaluator_eligibility()["rules"]
    blockers = {
        row["rule_id"]: row["implementation_blocker"]
        for row in rows
        if row["rule_id"]
        in {
            "rule::boom_claims_u_shape",
            "rule::trough_claims_reversal",
            "rule::trough_labor_reversal",
            "rule::recovery_durable_goods_new_orders",
        }
    }

    assert set(blockers.values()) == {
        "reference_window_not_preregistered",
        "turning_point_window_not_preregistered",
        "persistence_and_lookback_not_preregistered",
    }
