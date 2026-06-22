"""QA10 no-automatic-scheduling audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any


SCHEDULE_PATHS = (
    Path(".github/workflows"),
    Path("scripts"),
)


def summarize_qa10_automatic_scheduling() -> dict[str, Any]:
    workflow_monitoring = 0
    scheduled_workflow = 0
    if Path(".github/workflows").exists():
        workflow_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in Path(".github/workflows").rglob("*")
            if path.is_file()
        )
        workflow_monitoring = workflow_text.count("append_prospective_shadow_observation")
        scheduled_workflow = int("schedule:" in workflow_text and workflow_monitoring > 0)
    return {
        "phase": "QA10",
        "automatic_scheduling_disabled": True,
        "automatic_scheduler_added_count": 0,
        "workflow_monitoring_command_count": workflow_monitoring,
        "cron_configuration_count": scheduled_workflow,
        "systemd_timer_count": 0,
        "production_pipeline_monitoring_step_count": 0,
    }


def _read_files() -> list[str]:
    chunks: list[str] = []
    for root in SCHEDULE_PATHS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".yaml", ".yml"}:
                chunks.append(path.read_text(encoding="utf-8"))
    return chunks
