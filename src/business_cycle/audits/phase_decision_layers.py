"""QA2 decision-layer contract checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def summarize_phase_decision_layer_contract(
    path: str | Path = "specs/audits/phase_decision_layer_contract.yaml",
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["phase_decision_layer_contract"]
    layers = contract["layers"]
    data_only_layers = [
        layer for layer in layers if layer["layer_id"] == "sequence_constrained_data_only_decision"
    ]
    data_only_external = sum(
        bool(layer.get("allows_external_context")) for layer in data_only_layers
    )
    data_only_display = sum(bool(layer.get("allows_display_hint")) for layer in data_only_layers)
    display_changed = sum(
        bool(layer.get("decision_impact_allowed"))
        for layer in layers
        if layer["layer_id"] == "display_stage_hint"
    )
    undeclared = sum(not layer.get("provenance_complete") for layer in layers)
    return {
        "phase": "QA2",
        "decision_layer_count": len(layers),
        "decision_layer_contract_ready": data_only_external == 0
        and data_only_display == 0
        and display_changed == 0
        and undeclared == 0,
        "data_only_layer_read_external_context_count": data_only_external,
        "data_only_layer_read_display_hint_count": data_only_display,
        "display_layer_changed_decision_count": display_changed,
        "undeclared_decision_dependency_count": undeclared,
        "layers": layers,
        "result": "passed"
        if data_only_external == data_only_display == display_changed == undeclared == 0
        else "blocked",
    }
