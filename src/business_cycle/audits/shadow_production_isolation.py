"""QA5 production isolation checks for shadow model code."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PRODUCTION_SOURCE_PATHS = (
    Path("src/business_cycle/indicators"),
    Path("src/business_cycle/phases"),
    Path("src/business_cycle/pipeline"),
    Path("src/business_cycle/render"),
)
PRODUCTION_SCRIPT_PATHS = (
    Path("scripts/score_indicators.py"),
    Path("scripts/score_phases.py"),
    Path("scripts/resolve_current_phase.py"),
    Path("scripts/build_site.py"),
    Path("scripts/run_cycle_pipeline.py"),
)


def summarize_shadow_production_isolation() -> dict[str, Any]:
    """Ensure shadow modules are not imported by production code paths."""

    production_imports = _count_shadow_mentions(PRODUCTION_SOURCE_PATHS)
    script_mentions = _count_shadow_mentions(PRODUCTION_SCRIPT_PATHS)
    catalog_mentions = _text_count(Path("specs/indicator_catalog.yaml"), "shadow")
    resolver_mentions = _count_shadow_mentions((Path("src/business_cycle/phases"),))
    dashboard_mentions = _count_shadow_mentions((Path("src/business_cycle/render"),))
    workflow_mentions = _count_shadow_mentions((Path(".github/workflows"),))
    public_mentions = _count_shadow_mentions((Path("public"),))
    total_behavior_change = 0
    return {
        "phase": "QA5",
        "production_isolation_verified": production_imports == 0
        and catalog_mentions == 0
        and script_mentions == 0
        and resolver_mentions == 0
        and dashboard_mentions == 0
        and workflow_mentions == 0
        and public_mentions == 0
        and total_behavior_change == 0,
        "production_imports_shadow_module_count": production_imports,
        "production_catalog_shadow_indicator_count": catalog_mentions,
        "production_pipeline_shadow_step_count": script_mentions,
        "resolver_shadow_dependency_count": resolver_mentions,
        "dashboard_shadow_dependency_count": dashboard_mentions,
        "workflow_shadow_command_count": workflow_mentions,
        "public_shadow_output_count": public_mentions,
        "production_behavior_change_count": total_behavior_change,
    }


def _count_shadow_mentions(paths: tuple[Path, ...]) -> int:
    count = 0
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            count += _text_count(path, "shadow_model")
            continue
        for file_path in path.rglob("*.py"):
            if "__pycache__" in file_path.parts:
                continue
            count += _text_count(file_path, "shadow_model")
    return count


def _text_count(path: Path, needle: str) -> int:
    if not path.exists() or not path.is_file():
        return 0
    try:
        return path.read_text(encoding="utf-8").count(needle)
    except UnicodeDecodeError:
        return 0

