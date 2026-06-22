from __future__ import annotations

from business_cycle.audits.qa10_automatic_scheduling import (
    summarize_qa10_automatic_scheduling,
)


def test_no_prospective_automatic_scheduling() -> None:
    summary = summarize_qa10_automatic_scheduling()

    assert summary["automatic_scheduling_disabled"] is True
    assert summary["automatic_scheduler_added_count"] == 0
    assert summary["workflow_monitoring_command_count"] == 0
    assert summary["cron_configuration_count"] == 0
    assert summary["systemd_timer_count"] == 0
    assert summary["production_pipeline_monitoring_step_count"] == 0
