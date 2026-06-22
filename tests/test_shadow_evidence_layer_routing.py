from __future__ import annotations

from business_cycle.audits.shadow_evidence_layer_routing import (
    summarize_shadow_evidence_layer_routing,
)


def test_shadow_evidence_layer_routing_has_no_cross_layer_violations() -> None:
    summary = summarize_shadow_evidence_layer_routing()

    assert summary["layer_routing_contract_ready"] is True
    assert summary["role_without_primary_layer_count"] == 0
    assert summary["role_with_multiple_primary_layers_count"] == 0
    assert summary["prohibited_cross_layer_route_count"] == 0
    assert summary["portfolio_feedback_to_phase_count"] == 0
    assert summary["transition_watch_direct_phase_confirmation_count"] == 0
