from __future__ import annotations

from business_cycle.audits.formal_model_layers import (
    summarize_formal_model_layer_architecture,
)


def test_formal_model_layers_have_separated_boundaries() -> None:
    summary = summarize_formal_model_layer_architecture()

    assert summary["formal_model_layer_architecture_ready"] is True
    assert summary["layer_count"] == 5
    assert summary["portfolio_policy_to_phase_feedback_count"] == 0
    assert summary["regime_score_mixed_into_phase_score_count"] == 0
    assert summary["shock_overlay_direct_phase_override_count"] == 0
    assert summary["transition_evidence_direct_trade_signal_count"] == 0
    assert summary["undeclared_cross_layer_dependency_count"] == 0


def test_portfolio_layer_cannot_change_phase() -> None:
    layers = summarize_formal_model_layer_architecture()["layers"]
    portfolio = next(layer for layer in layers if layer["layer_id"] == "portfolio_policy_layer")

    assert portfolio["may_change_formal_phase"] is False
    assert portfolio["live_decision_allowed"] is False

