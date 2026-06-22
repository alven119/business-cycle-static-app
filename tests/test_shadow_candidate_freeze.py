from __future__ import annotations

from business_cycle.audits.shadow_candidate_freeze import (
    summarize_book_faithful_shadow_candidate_freeze,
)


def test_shadow_candidate_freeze_is_reproducible_and_not_decision_freeze() -> None:
    summary = summarize_book_faithful_shadow_candidate_freeze()

    assert summary["shadow_candidate_freeze_ready"] is True
    assert summary["shadow_freeze_hash_valid"] is True
    assert summary["shadow_freeze_missing_file_count"] == 0
    assert summary["shadow_freeze_hash_mismatch_count"] == 0
    assert summary["secret_in_shadow_freeze_count"] == 0
    assert summary["decision_parameter_frozen_count"] == 0
    assert summary["holdout_registered"] is False
    assert summary["production_migration_allowed"] is False
    assert summary["aggregation_rule_frozen"] is False
