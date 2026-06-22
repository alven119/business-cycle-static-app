from __future__ import annotations

from business_cycle.audits.prospective_capability_matrix import (
    summarize_prospective_capability_matrix,
)


def test_capability_matrix_has_no_downstream_readiness_leakage() -> None:
    summary = summarize_prospective_capability_matrix()

    assert summary["prospective_capability_matrix_ready"] is True
    assert summary["capability_cell_count"] > 0
    assert summary["capability_unknown_count"] == 0
    assert summary["capability_inconsistent_count"] == 0
    assert summary["downstream_ready_without_upstream_ready_count"] == 0
    assert summary["candidate_ready_without_phase_evidence_count"] == 0
    assert summary["production_ready_without_candidate_ready_count"] == 0

