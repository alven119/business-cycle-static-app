from __future__ import annotations

from business_cycle.audits.qa12_production_isolation import (
    summarize_qa12_production_isolation,
)


def test_qa12_production_isolation_and_no_scheduler() -> None:
    summary = summarize_qa12_production_isolation()

    assert summary["production_isolation_verified"] is True
    assert summary["automatic_scheduling_disabled"] is True
    assert summary["automatic_scheduler_added_count"] == 0
    assert summary["workflow_monitoring_command_count"] == 0
    assert summary["cron_configuration_count"] == 0
    assert summary["systemd_timer_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["real_registry_record_written_count"] == 0
    assert summary["production_imports_manual_start_count"] == 0
    assert summary["production_behavior_change_count"] == 0

