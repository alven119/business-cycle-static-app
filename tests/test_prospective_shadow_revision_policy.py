from __future__ import annotations

from business_cycle.audits.prospective_shadow_revision_policy import (
    summarize_prospective_shadow_revision_policy,
)


def test_prospective_shadow_revision_policy_blocks_real_revised_records() -> None:
    summary = summarize_prospective_shadow_revision_policy()

    assert summary["revision_policy_ready"] is True
    assert summary["revised_mode_real_registry_record_count"] == 0
    assert summary["proxy_mode_real_registry_record_count"] == 0
    assert summary["initial_release_misclassified_count"] == 0
    assert summary["mixed_mode_real_registry_record_count"] == 0
    assert summary["original_record_overwrite_count"] == 0
    assert summary["correction_without_lineage_count"] == 0
