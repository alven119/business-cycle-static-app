from __future__ import annotations

from business_cycle.audits.model_freeze_lineage import summarize_model_freeze_lineage


def test_model_freeze_lineage_preserves_prior_artifact() -> None:
    summary = summarize_model_freeze_lineage()

    assert summary["freeze_lineage_ready"] is True
    assert summary["prior_freeze_artifact_preserved"] is True
    assert summary["silent_freeze_rewrite_count"] == 0
    assert summary["changed_hash_without_lineage_count"] == 0
    assert summary["decision_active_change_without_new_model_version_count"] == 0
