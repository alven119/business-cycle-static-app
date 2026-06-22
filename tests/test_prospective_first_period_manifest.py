from __future__ import annotations

from business_cycle.shadow_model.prospective_period_manifest import (
    summarize_first_period_manifest,
)


def test_first_period_manifest_preserves_canonical_dates() -> None:
    summary = summarize_first_period_manifest()

    assert summary["first_period_manifest_ready"] is True
    assert summary["observation_period"] == "2026-07"
    assert summary["canonical_as_of"] == "2026-08-31"
    assert summary["manifest_role_count"] == 40
    assert summary["manifest_major_group_count"] == 24
    assert summary["role_without_release_rule_count"] == 0
    assert summary["manifest_duplicate_role_count"] == 0
    assert summary["derived_manifest_without_inputs_count"] == 0
    assert summary["earliest_append_before_canonical_as_of_count"] == 0
    assert summary["manifest_hash_valid"] is True

