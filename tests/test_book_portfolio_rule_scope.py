from __future__ import annotations

from business_cycle.audits.qa4_scope_contracts import summarize_book_portfolio_rule_scope


def test_book_portfolio_rules_are_research_scope_only() -> None:
    summary = summarize_book_portfolio_rule_scope()

    assert summary["book_portfolio_rule_scope_ready"] is True
    assert summary["book_strategy_count"] == 5
    assert summary["book_rule_spec_ready"] is True
    assert summary["book_rule_execution_ready"] is False
    assert summary["generic_bond_substitution_count"] == 0
    assert summary["monthly_rebalance_misclassified_as_book_baseline_count"] == 0
    assert summary["boom_year_schedule_used_as_phase_transition_count"] == 0

