from __future__ import annotations

from business_cycle.audits.qa0_integrity_audit import run_qa0_integrity_audit


def test_productivity_inflation_regime_gap_blocks_regime_claims() -> None:
    summary = run_qa0_integrity_audit()

    assert summary["regime_rule_count"] >= 3
    assert summary["regime_indicator_count"] >= 6
    assert summary["formal_regime_layer_ready"] is False
    assert summary["regime_aware_portfolio_policy_ready"] is False

