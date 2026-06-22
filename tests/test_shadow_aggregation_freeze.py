from __future__ import annotations

from business_cycle.audits.shadow_aggregation_freeze import (
    summarize_shadow_aggregation_freeze,
)


def test_shadow_aggregation_freeze_is_reproducible_and_scope_only() -> None:
    summary = summarize_shadow_aggregation_freeze()

    assert summary["shadow_aggregation_freeze_ready"] is True
    assert summary["aggregation_freeze_hash_valid"] is True
    assert summary["aggregation_freeze_missing_file_count"] == 0
    assert summary["aggregation_freeze_hash_mismatch_count"] == 0
    assert summary["secret_in_aggregation_freeze_count"] == 0
    assert summary["numeric_weight_frozen_count"] == 0
    assert summary["threshold_frozen_count"] == 0
    assert summary["holdout_registered"] is False
