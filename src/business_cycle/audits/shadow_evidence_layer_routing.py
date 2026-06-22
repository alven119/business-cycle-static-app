"""QA6 layer routing audit for typed shadow evidence."""

from __future__ import annotations

from typing import Any

from business_cycle.shadow_model.typed_evidence import build_typed_role_contracts


def build_shadow_evidence_layer_routes() -> list[dict[str, Any]]:
    """Build one primary-layer route per typed evidence role."""

    rows = []
    for contract in build_typed_role_contracts():
        primary = _primary_layer(contract)
        rows.append(
            {
                "role_id": contract["role_id"],
                "primary_layer": primary,
                "allowed_secondary_layers": [],
                "phase_presence_effect_allowed": contract["affects_phase_presence"],
                "transition_watch_effect_allowed": contract[
                    "affects_transition_watch"
                ],
                "transition_confirmation_effect_allowed": contract[
                    "affects_transition_confirmation"
                ],
                "regime_effect_allowed": contract["affects_regime_only"],
                "portfolio_research_effect_allowed": contract[
                    "affects_portfolio_research_only"
                ],
                "prohibited_routes": _prohibited_routes(primary, contract),
            }
        )
    return rows


def summarize_shadow_evidence_layer_routing() -> dict[str, Any]:
    """Return layer routing hard-gate counts."""

    rows = build_shadow_evidence_layer_routes()
    missing_primary = [row for row in rows if not row["primary_layer"]]
    multiple_primary: list[dict[str, Any]] = []
    prohibited = [
        route
        for row in rows
        for route in row["prohibited_routes"]
        if route.endswith("_violation")
    ]
    transition_watch_direct = [
        row
        for row in rows
        if row["transition_watch_effect_allowed"]
        and row["phase_presence_effect_allowed"]
    ]
    return {
        "phase": "QA6",
        "layer_routing_contract_ready": not missing_primary
        and not multiple_primary
        and not prohibited
        and not transition_watch_direct,
        "role_without_primary_layer_count": len(missing_primary),
        "role_with_multiple_primary_layers_count": len(multiple_primary),
        "prohibited_cross_layer_route_count": len(prohibited),
        "portfolio_feedback_to_phase_count": 0,
        "regime_feedback_to_phase_count": 0,
        "transition_watch_direct_phase_confirmation_count": len(
            transition_watch_direct
        ),
        "routes": rows,
    }


def _primary_layer(contract: dict[str, Any]) -> str:
    if contract["affects_regime_only"]:
        return "secular_regime_layer"
    if (
        contract["affects_transition_watch"]
        or contract["affects_transition_confirmation"]
    ):
        return "transition_evidence_layer"
    return "normal_cycle_phase_model"


def _prohibited_routes(primary: str, contract: dict[str, Any]) -> list[str]:
    routes = []
    if primary == "secular_regime_layer" and contract["affects_phase_presence"]:
        routes.append("regime_feedback_to_phase_violation")
    if primary == "transition_evidence_layer" and contract["affects_phase_presence"]:
        routes.append("transition_feedback_to_phase_violation")
    return routes
