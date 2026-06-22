from __future__ import annotations

from business_cycle.audits.qa4_scope_contracts import (
    summarize_exogenous_shock_overlay_scope,
)


def test_shock_overlay_is_scoped_but_not_runtime_override() -> None:
    summary = summarize_exogenous_shock_overlay_scope()

    assert summary["shock_overlay_scope_ready"] is True
    assert summary["shock_overlay_scope_defined"] is True
    assert summary["shock_overlay_formal_runtime_ready"] is False
    assert summary["shock_overlay_direct_phase_override_allowed"] is False
    assert summary["shock_overlay_direct_portfolio_action_allowed"] is False
    assert summary["covid_specific_general_rule_count"] == 0

