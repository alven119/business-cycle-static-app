from __future__ import annotations

from business_cycle.audits.qa4_scope_contracts import summarize_secular_regime_scope


def test_regime_scope_does_not_mix_into_phase_score() -> None:
    summary = summarize_secular_regime_scope()

    assert summary["secular_regime_scope_ready"] is True
    assert summary["regime_scope_item_count"] == 3
    assert summary["regime_indicator_role_count"] == 6
    assert summary["regime_formal_runtime_ready"] is False
    assert summary["regime_phase_score_integration_allowed"] is False
    assert summary["regime_portfolio_research_input_allowed"] is True
    assert summary["regime_live_allocation_allowed"] is False

