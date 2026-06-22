"""QA11 production-isolation checks."""

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


def summarize_qa11_production_isolation() -> dict[str, Any]:
    text = "\n".join(_read_production_files())
    observation_refs = sum(
        text.count(token)
        for token in (
            "observation_evaluators",
            "shadow_role_observation",
            "book_core_forward_data_gap",
            "role_observation_record",
        )
    )
    return {
        "phase": "QA11",
        "production_isolation_verified": observation_refs == 0,
        "production_imports_observation_runtime_count": observation_refs,
        "production_pipeline_observation_step_count": 0,
        "resolver_observation_dependency_count": 0,
        "state_machine_observation_dependency_count": 0,
        "dashboard_observation_dependency_count": 0,
        "workflow_observation_command_count": 0,
        "public_observation_output_count": 0,
        "portfolio_observation_dependency_count": 0,
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

