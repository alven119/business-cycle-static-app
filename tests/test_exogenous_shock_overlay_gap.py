from __future__ import annotations

from business_cycle.audits.qa0_integrity_audit import run_qa0_integrity_audit


def test_exogenous_shock_overlay_spec_ready_but_runtime_blocked() -> None:
    summary = run_qa0_integrity_audit()

    assert summary["shock_overlay_spec_ready"] is True
    assert summary["formal_shock_runtime_ready"] is False
    assert summary["covid_generalization_allowed"] is False
    assert summary["normal_cycle_rule_preserved"] is True

