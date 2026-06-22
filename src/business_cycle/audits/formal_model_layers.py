"""QA4 formal model layer architecture audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_LAYER_PATH = Path("specs/audits/formal_model_layer_architecture.yaml")


def summarize_formal_model_layer_architecture(
    path: str | Path = DEFAULT_LAYER_PATH,
) -> dict[str, Any]:
    """Validate declared layer boundaries and cross-layer prohibitions."""

    spec = _load_spec(path)
    layers = spec["layers"]
    layer_ids = {layer["layer_id"] for layer in layers}
    undeclared_deps = [
        dependency
        for layer in layers
        for dependency in layer.get("dependency_layers", [])
        if dependency not in layer_ids
    ]
    portfolio_feedback = [
        layer
        for layer in layers
        if layer["layer_id"] == "portfolio_policy_layer"
        and layer["may_change_formal_phase"] is True
    ]
    regime_mixed = [
        layer
        for layer in layers
        if layer["layer_id"] == "secular_regime_layer"
        and layer["may_change_formal_phase"] is True
    ]
    shock_override = [
        layer
        for layer in layers
        if layer["layer_id"] == "exogenous_shock_overlay"
        and layer["may_change_formal_phase"] is True
    ]
    transition_trade = [
        layer
        for layer in layers
        if layer["layer_id"] == "transition_evidence_layer"
        and (
            "trade signal" not in layer.get("prohibited_outputs", [])
            or layer["live_decision_allowed"] is True
        )
    ]
    return {
        "phase": "QA4",
        "formal_model_layer_architecture_ready": not (
            portfolio_feedback
            or regime_mixed
            or shock_override
            or transition_trade
            or undeclared_deps
        ),
        "layer_count": len(layers),
        "portfolio_policy_to_phase_feedback_count": len(portfolio_feedback),
        "regime_score_mixed_into_phase_score_count": len(regime_mixed),
        "shock_overlay_direct_phase_override_count": len(shock_override),
        "transition_evidence_direct_trade_signal_count": len(transition_trade),
        "undeclared_cross_layer_dependency_count": len(undeclared_deps),
        "layers": layers,
    }


def _load_spec(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload["formal_model_layer_architecture"]

