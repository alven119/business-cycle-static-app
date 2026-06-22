from __future__ import annotations

from business_cycle.audits.evidence_evaluability import (
    summarize_evidence_evaluability_status_contract,
)


def test_primary_statuses_are_mutually_exclusive() -> None:
    summary = summarize_evidence_evaluability_status_contract()

    assert summary["role_count"] == 40
    assert summary["primary_status_count_sum"] == 40
    assert summary["role_without_primary_status_count"] == 0
    assert summary["role_with_multiple_primary_status_count"] == 0
    assert summary["primary_secondary_semantics_valid"] is True


def test_secondary_blockers_overlap_primary_statuses() -> None:
    summary = summarize_evidence_evaluability_status_contract()

    assert summary["threshold_secondary_blocker_count"] == 24
    assert summary["threshold_primary_blocker_count"] == 0
    assert summary["blocker_count_misinterpreted_as_mutually_exclusive_count"] == 0
    assert summary["primary_status_counts"]["evaluable"] == 1
