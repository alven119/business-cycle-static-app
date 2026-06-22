from __future__ import annotations

from business_cycle.audits.phase_decision_layers import (
    summarize_phase_decision_layer_contract,
)


def test_data_only_layer_cannot_read_context_or_display_hints() -> None:
    summary = summarize_phase_decision_layer_contract()

    assert summary["decision_layer_contract_ready"] is True
    assert summary["data_only_layer_read_external_context_count"] == 0
    assert summary["data_only_layer_read_display_hint_count"] == 0
    assert summary["display_layer_changed_decision_count"] == 0
    assert summary["undeclared_decision_dependency_count"] == 0
