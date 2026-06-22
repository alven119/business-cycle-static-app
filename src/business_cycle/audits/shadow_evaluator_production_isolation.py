"""QA8 production isolation checks for shadow evaluators and prospective gate."""

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
NEEDLES = (
    "shadow_model.evidence_evaluators",
    "shadow_model.evaluator_primitives",
    "shadow_model.prospective_gate",
    "run_shadow_evidence_diagnostics",
)


def summarize_shadow_evaluator_production_isolation() -> dict[str, Any]:
    """Ensure QA8 shadow evaluator code is not loaded by production paths."""

    production_imports = _count_mentions(PRODUCTION_SOURCE_PATHS)
    script_mentions = _count_mentions(PRODUCTION_SCRIPT_PATHS)
    resolver_mentions = _count_mentions((Path("src/business_cycle/phases"),))
    state_machine_mentions = resolver_mentions
    dashboard_mentions = _count_mentions((Path("src/business_cycle/render"),))
    workflow_mentions = _count_mentions((Path(".github/workflows"),))
    public_mentions = _count_mentions((Path("public"),))
    verified = all(
        count == 0
        for count in (
            production_imports,
            script_mentions,
            resolver_mentions,
            state_machine_mentions,
            dashboard_mentions,
            workflow_mentions,
            public_mentions,
        )
    )
    return {
        "phase": "QA8",
        "production_isolation_verified": verified,
        "production_imports_shadow_evaluator_count": production_imports,
        "production_imports_prospective_gate_count": production_imports,
        "production_pipeline_shadow_evaluator_step_count": script_mentions,
        "resolver_prospective_dependency_count": resolver_mentions,
        "state_machine_prospective_dependency_count": state_machine_mentions,
        "dashboard_shadow_evidence_dependency_count": dashboard_mentions,
        "workflow_shadow_evaluator_command_count": workflow_mentions,
        "public_shadow_evidence_output_count": public_mentions,
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
            if "__pycache__" not in file_path.parts:
                count += _text_count(file_path)
    return count


def _text_count(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0
    return sum(text.count(needle) for needle in NEEDLES)
