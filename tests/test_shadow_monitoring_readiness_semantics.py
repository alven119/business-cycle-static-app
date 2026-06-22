from __future__ import annotations

from business_cycle.audits.shadow_monitoring_readiness import (
    summarize_shadow_monitoring_readiness,
)


def test_shadow_monitoring_readiness_semantics_are_split() -> None:
    summary = summarize_shadow_monitoring_readiness()

    assert summary["evidence_recording_runtime_ready"] is True
    assert summary["single_role_observation_monitoring_ready"] is True
    assert summary["candidate_monitoring_allowed"] is False
    assert summary["runtime_ready_mislabeled_major_group_ready_count"] == 0
    assert summary["observation_ready_mislabeled_phase_evidence_ready_count"] == 0
    assert summary["phase_evidence_ready_mislabeled_candidate_ready_count"] == 0

