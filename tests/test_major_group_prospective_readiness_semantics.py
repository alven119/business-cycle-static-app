from __future__ import annotations

from business_cycle.audits.major_group_prospective_readiness import (
    summarize_major_group_prospective_readiness,
)


def test_major_group_readiness_semantics_are_not_mixed() -> None:
    summary = summarize_major_group_prospective_readiness()

    assert summary["readiness_semantics_reconciled"] is True
    assert summary["major_group_count"] == 24
    assert summary["observation_contract_ready_group_count"] == 19
    assert summary["adapter_ready_group_count"] == 19
    assert summary["live_preflight_ready_group_count"] == 19
    assert summary["all_major_groups_observation_contract_ready"] is False
    assert summary["period_complete_group_count"] == 0
    assert summary["phase_evidence_ready_group_count"] == 0
    assert summary["candidate_input_complete_group_count"] == 0
    assert summary["partial_group_mislabeled_complete_count"] == 0
    assert summary["contract_ready_mislabeled_live_ready_count"] == 0
    assert summary["live_ready_mislabeled_period_complete_count"] == 0
    assert summary["observation_ready_mislabeled_phase_evidence_ready_count"] == 0
    assert summary["phase_evidence_ready_mislabeled_candidate_complete_count"] == 0
