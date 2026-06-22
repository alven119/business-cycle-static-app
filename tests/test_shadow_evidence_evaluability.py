from __future__ import annotations

from business_cycle.audits.evidence_evaluability import summarize_evidence_evaluability


def test_shadow_evidence_evaluability_classifies_all_roles() -> None:
    summary = summarize_evidence_evaluability()

    assert summary["evaluability_root_cause_audit_ready"] is True
    assert summary["role_count"] == 40
    assert summary["evaluable_role_count"] == 0
    assert summary["reason_classified_role_count"] == 40
    assert summary["unclassified_non_evaluable_reason_count"] == 0
    assert summary["global_evaluability_kill_switch_count"] == 0
    assert summary["evaluable_role_without_complete_gate_count"] == 0


def test_shadow_evidence_evaluability_has_no_global_kill_switch() -> None:
    reasons = summarize_evidence_evaluability()["non_evaluable_reason_counts"]

    assert reasons["threshold_not_preregistered"] > 0
    assert reasons["source_not_verified"] > 0
    assert reasons["transformation_raw_only"] > 0
