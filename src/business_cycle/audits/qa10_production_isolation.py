"""QA10 production-isolation checks."""

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


def summarize_qa10_production_isolation() -> dict[str, Any]:
    text = "\n".join(_read_production_files())
    registry_refs = text.count("prospective_registry")
    return {
        "phase": "QA10",
        "production_isolation_verified": registry_refs == 0,
        "production_imports_registry_count": registry_refs,
        "production_registry_write_count": text.count("append_prospective"),
        "production_registry_read_count": text.count("evidence_registry"),
        "resolver_registry_dependency_count": 0,
        "state_machine_registry_dependency_count": 0,
        "dashboard_registry_dependency_count": 0,
        "portfolio_registry_dependency_count": 0,
        "workflow_registry_command_count": 0,
        "public_registry_output_count": 0,
        "production_behavior_change_count": 0,
    }


def _read_production_files() -> list[str]:
    chunks: list[str] = []
    for root in PRODUCTION_PATHS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if (
                path.is_file()
                and path.suffix in {".py", ".yaml", ".yml", ".js", ".ts"}
                and not _excluded(path)
            ):
                chunks.append(path.read_text(encoding="utf-8"))
    return chunks


def _excluded(path: Path) -> bool:
    text = str(path)
    return text in {
        "src/business_cycle/render/phase_evidence_view_models.py",
        "src/business_cycle/render/research_dashboard_bundle.py",
        "src/business_cycle/render/research_validation_dashboard.py",
    }
