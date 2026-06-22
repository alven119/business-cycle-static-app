from __future__ import annotations

from business_cycle.audits.prospective_protocol_versioning import (
    summarize_prospective_protocol_versioning,
)


def test_prospective_protocol_versioning_requires_no_successor_when_alpha4_valid() -> None:
    summary = summarize_prospective_protocol_versioning()

    assert summary["protocol_versioning_ready"] is True
    assert summary["evaluator_freeze_changed"] is False
    assert summary["successor_model_version_required"] is False
    assert summary["required_successor_missing_count"] == 0
    assert summary["silent_freeze_update_count"] == 0
    assert summary["start_date_moved_earlier_count"] == 0
    assert summary["protocol_version_lineage_valid"] is True
