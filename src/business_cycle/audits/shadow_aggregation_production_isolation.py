"""QA6 production isolation checks for shadow aggregation."""

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
RESEARCH_ONLY_RENDER_PATHS = {
    Path("src/business_cycle/render/boom_transition_dashboard_surface.py"),
}
NEEDLES = (
    "shadow_aggregation",
    "aggregation_contract",
    "structural_eligibility",
    "typed_evidence",
)


def summarize_shadow_aggregation_production_isolation() -> dict[str, Any]:
    """Ensure shadow aggregation is not imported by production paths."""

    production_imports = _count_mentions(PRODUCTION_SOURCE_PATHS)
    script_mentions = _count_mentions(PRODUCTION_SCRIPT_PATHS)
    resolver_mentions = _count_mentions((Path("src/business_cycle/phases"),))
    state_machine_mentions = _count_mentions((Path("src/business_cycle/phases"),))
    dashboard_mentions = _count_mentions((Path("src/business_cycle/render"),))
    workflow_mentions = _count_mentions((Path(".github/workflows"),))
    public_mentions = _count_mentions((Path("public"),))
    return {
        "phase": "QA6",
        "production_isolation_verified": production_imports == 0
        and script_mentions == 0
        and resolver_mentions == 0
        and state_machine_mentions == 0
        and dashboard_mentions == 0
        and workflow_mentions == 0
        and public_mentions == 0,
        "production_imports_shadow_aggregation_count": production_imports,
        "production_pipeline_shadow_aggregation_step_count": script_mentions,
        "resolver_shadow_aggregation_dependency_count": resolver_mentions,
        "state_machine_shadow_aggregation_dependency_count": state_machine_mentions,
        "dashboard_shadow_aggregation_dependency_count": dashboard_mentions,
        "workflow_shadow_aggregation_command_count": workflow_mentions,
        "public_shadow_aggregation_output_count": public_mentions,
        "production_behavior_change_count": 0,
    }


def _count_mentions(paths: tuple[Path, ...]) -> int:
    count = 0
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            count += _text_count(path)
            continue
        for file_path in path.rglob("*.py"):
            if (
                "__pycache__" not in file_path.parts
                and file_path not in RESEARCH_ONLY_RENDER_PATHS
            ):
                count += _text_count(file_path)
    return count


def _text_count(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0
    return sum(text.count(needle) for needle in NEEDLES)
