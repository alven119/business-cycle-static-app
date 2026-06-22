from __future__ import annotations

from business_cycle.shadow_model.manual_preview_bundle import (
    summarize_manual_preview_bundle,
)


def test_manual_preview_bundle_is_preview_only() -> None:
    summary = summarize_manual_preview_bundle()

    assert summary["manual_preview_bundle_ready"] is True
    assert summary["preview_bundle_count"] == 1
    assert summary["preview_role_record_count"] == 40
    assert summary["preview_group_count"] == 24
    assert summary["preview_record_with_real_registry_id_count"] == 0
    assert summary["preview_record_appended_count"] == 0
    assert summary["prohibited_decision_field_count"] == 0
    assert summary["preview_candidate_phase_count"] == 0
    assert summary["bundle"]["registry_write_attempted"] is False

