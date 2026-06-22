from __future__ import annotations

from business_cycle.shadow_model.typed_evidence import (
    build_typed_role_contracts,
    summarize_typed_book_evidence_contract,
)


def test_typed_evidence_contract_covers_all_roles() -> None:
    summary = summarize_typed_book_evidence_contract()

    assert summary["typed_evidence_contract_ready"] is True
    assert summary["typed_role_count"] == 40
    assert summary["untyped_role_count"] == 0
    assert summary["transition_signal_used_as_phase_support_count"] == 0
    assert summary["regime_signal_used_as_phase_support_count"] == 0
    assert summary["raw_transform_promoted_to_directional_signal_count"] == 0


def test_typed_evidence_keeps_watch_and_ending_out_of_phase_presence() -> None:
    rows = {row["role_id"]: row for row in build_typed_role_contracts()}

    assert rows["boom_claims_u_shape"]["typed_evidence_family"] == "boom_ending"
    assert rows["boom_claims_u_shape"]["affects_phase_presence"] is False
    assert rows["trough_policy_financial_not_sufficient_alone"][
        "typed_evidence_family"
    ] == "recovery_watch"
    assert rows["trough_policy_financial_not_sufficient_alone"][
        "affects_phase_presence"
    ] is False
