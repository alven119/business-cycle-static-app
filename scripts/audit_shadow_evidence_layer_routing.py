from __future__ import annotations

from business_cycle.audits.shadow_evidence_layer_routing import (
    summarize_shadow_evidence_layer_routing,
)


def main() -> None:
    summary = summarize_shadow_evidence_layer_routing()
    for key in (
        "phase",
        "layer_routing_contract_ready",
        "role_without_primary_layer_count",
        "role_with_multiple_primary_layers_count",
        "prohibited_cross_layer_route_count",
        "portfolio_feedback_to_phase_count",
        "regime_feedback_to_phase_count",
        "transition_watch_direct_phase_confirmation_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
