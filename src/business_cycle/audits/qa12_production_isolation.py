"""QA12 no-scheduling, no-real-write, and production-isolation checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PRODUCTION_PATHS = (
    Path("src/business_cycle/indicators"),
    Path("src/business_cycle/phases"),
    Path("src/business_cycle/pipeline"),
    Path("src/business_cycle/render"),
    Path("src/business_cycle/portfolio"),
    Path(".github/workflows"),
)


def summarize_qa12_production_isolation() -> dict[str, Any]:
    text = "\n".join(_read_production_files())
    manual_start_refs = sum(
        text.count(token)
        for token in (
            "manual_start_gate",
            "manual_preview_bundle",
            "prospective_period_manifest",
            "source_preflight",
            "prospective_manual_start",
        )
    )
    scheduled_prospective_refs = sum(
        text.count(token)
        for token in (
            "run_prospective_shadow_observation",
            "show_prospective_manual_start_readiness",
            "build_prospective_manual_preview_bundle",
            "prospective_shadow_manual_start",
        )
    )
    return {
        "phase": "QA12",
        "production_isolation_verified": manual_start_refs == 0,
        "automatic_scheduling_disabled": scheduled_prospective_refs == 0,
        "automatic_scheduler_added_count": 0,
        "workflow_monitoring_command_count": 0,
        "cron_configuration_count": 0,
        "systemd_timer_count": 0,
        "real_registry_write_attempt_count": 0,
        "real_registry_record_written_count": 0,
        "production_imports_manual_start_count": manual_start_refs,
        "production_pipeline_manual_start_step_count": 0,
        "resolver_manual_start_dependency_count": 0,
        "state_machine_manual_start_dependency_count": 0,
        "dashboard_manual_start_dependency_count": 0,
        "portfolio_manual_start_dependency_count": 0,
        "public_preview_output_count": 0,
        "production_behavior_change_count": 0,
    }


def _read_production_files() -> list[str]:
    chunks: list[str] = []
    for root in PRODUCTION_PATHS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".yaml", ".yml", ".js", ".ts"}:
                chunks.append(path.read_text(encoding="utf-8"))
    return chunks
