from __future__ import annotations

from business_cycle.audits.prospective_registry_production_isolation import (
    summarize_prospective_registry_production_isolation,
)


def test_prospective_registry_production_isolation() -> None:
    summary = summarize_prospective_registry_production_isolation()

    assert summary["production_isolation_verified"] is True
    assert summary["production_imports_prospective_registry_count"] == 0
    assert summary["production_writes_prospective_registry_count"] == 0
    assert summary["workflow_prospective_command_count"] == 0
    assert summary["scheduled_prospective_job_count"] == 0
    assert summary["public_prospective_output_count"] == 0
    assert summary["production_behavior_change_count"] == 0
