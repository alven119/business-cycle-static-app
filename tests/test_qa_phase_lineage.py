from __future__ import annotations

from business_cycle.audits.qa_phase_lineage import summarize_qa_phase_lineage


def test_qa8_qa9_phase_lineage_is_valid() -> None:
    summary = summarize_qa_phase_lineage()

    assert summary["qa8_closure_artifact_count"] == 1
    assert summary["qa8_closure_passed"] is True
    assert summary["qa9_closure_artifact_count"] == 1
    assert summary["qa9_closure_passed"] is True
    assert summary["phase_sequence_gap_count"] == 0
    assert summary["freeze_parent_mismatch_count"] == 0
    assert summary["missing_phase_artifact_count"] == 0
    assert summary["silent_freeze_rewrite_count"] == 0
    assert summary["monitoring_freeze_parent_valid"] is True
    assert summary["qa8_qa9_lineage_valid"] is True
