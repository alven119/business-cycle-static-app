from __future__ import annotations

from business_cycle.shadow_model.forward_capture_contract import (
    summarize_forward_capture_contracts,
)


def test_forward_capture_contracts_cover_forward_ready_roles() -> None:
    summary = summarize_forward_capture_contracts()

    assert summary["forward_capture_contract_ready"] is True
    assert summary["ready_role_without_capture_contract_count"] == 0
    assert summary["capture_contract_without_role_count"] == 0
    assert summary["capture_contract_without_release_semantics_count"] == 0
    assert summary["derived_capture_without_complete_inputs_count"] == 0

