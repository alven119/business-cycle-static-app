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
    assert summary["qa11_observation_freeze_id"] == "book_faithful_shadow_v2_alpha5"
    assert (
        summary["qa11_observation_parent_freeze_id"]
        == "book_faithful_shadow_v2_alpha4"
    )
    assert summary["qa11_observation_freeze_hash_valid"] is True
    assert summary["qa12_manual_start_freeze_id"] == "prospective_shadow_manual_start_v1"
    assert (
        summary["qa12_manual_start_parent_model_freeze_id"]
        == "book_faithful_shadow_v2_alpha5"
    )
    assert (
        summary["qa12_manual_start_parent_monitoring_freeze_id"]
        == "prospective_shadow_monitoring_v1"
    )
    assert summary["qa12_manual_start_freeze_hash_valid"] is True
    assert summary["phase10_source_adapter_freeze_id"] == (
        "book_faithful_shadow_v2_alpha6"
    )
    assert (
        summary["phase10_source_adapter_parent_freeze_id"]
        == "book_faithful_shadow_v2_alpha5"
    )
    assert summary["phase10_source_adapter_freeze_hash_valid"] is True
    assert summary["phase10_qa12_freeze_unchanged"] is True
