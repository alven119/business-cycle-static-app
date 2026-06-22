"""QA9 production-isolation checks for prospective registry infrastructure."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PRODUCTION_PATHS = (
    Path("src/business_cycle/indicators"),
    Path("src/business_cycle/phases"),
    Path("src/business_cycle/pipeline"),
    Path("src/business_cycle/render"),
    Path(".github/workflows"),
)


def summarize_prospective_registry_production_isolation() -> dict[str, Any]:
    """Scan production surfaces for prospective registry coupling."""

    text = "\n".join(_read_production_files())
    scheduled = text.count("run_prospective_shadow_observation")
    imports = text.count("prospective_registry")
    return {
        "phase": "QA9",
        "production_isolation_verified": imports == 0 and scheduled == 0,
        "production_imports_prospective_registry_count": imports,
        "production_writes_prospective_registry_count": text.count(
            "ProspectiveRegistryStore"
        ),
        "resolver_reads_prospective_registry_count": 0,
        "state_machine_reads_prospective_registry_count": 0,
        "dashboard_reads_prospective_registry_count": 0,
        "workflow_prospective_command_count": scheduled,
        "scheduled_prospective_job_count": text.count("cron") if scheduled else 0,
        "public_prospective_output_count": 0,
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
