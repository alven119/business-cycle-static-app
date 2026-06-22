from __future__ import annotations

from business_cycle.audits.prospective_monitoring_freeze import (
    summarize_prospective_monitoring_freeze,
)


def test_prospective_monitoring_freeze_is_reproducible() -> None:
    summary = summarize_prospective_monitoring_freeze()

    assert summary["monitoring_infrastructure_freeze_ready"] is True
    assert summary["monitoring_freeze_hash_valid"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["automatic_scheduler_allowed"] is False
    assert summary["protocol_started"] is False
    assert summary["holdout_registered"] is False
