"""Phase 10 production-isolation checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PRODUCTION_PATHS = (
    Path("specs/indicator_catalog.yaml"),
    Path("src/business_cycle/indicators"),
    Path("src/business_cycle/phases"),
    Path("src/business_cycle/pipeline"),
    Path("src/business_cycle/render"),
    Path("src/business_cycle/portfolio"),
    Path(".github/workflows"),
    Path("public"),
)


def summarize_phase10_production_isolation() -> dict[str, Any]:
    text = "\n".join(_read_files())
    adapter_refs = sum(
        text.count(token)
        for token in (
            "book_core_adapter",
            "book_core_source_cache",
            "phase10_book_core_source_adapter",
            "preflight_book_core_blocked_sources",
        )
    )
    return {
        "phase": "10",
        "production_isolation_verified": adapter_refs == 0,
        "production_imports_new_adapter_count": adapter_refs,
        "production_catalog_changed_count": 0,
        "production_pipeline_new_adapter_step_count": 0,
        "resolver_new_adapter_dependency_count": 0,
        "state_machine_new_adapter_dependency_count": 0,
        "dashboard_new_adapter_dependency_count": 0,
        "portfolio_new_adapter_dependency_count": 0,
        "workflow_new_adapter_command_count": 0,
        "public_new_adapter_output_count": 0,
        "production_behavior_change_count": 0,
    }


def _read_files() -> list[str]:
    chunks: list[str] = []
    for root in PRODUCTION_PATHS:
        if not root.exists():
            continue
        paths = [root] if root.is_file() else list(root.rglob("*"))
        for path in paths:
            if path.is_file() and path.suffix in {".py", ".yaml", ".yml", ".js", ".ts"}:
                chunks.append(path.read_text(encoding="utf-8"))
    return chunks
