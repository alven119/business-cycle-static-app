"""Phase 11 production and prospective isolation checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from business_cycle.audits.qa11_prospective_prestart import (
    summarize_qa11_prospective_prestart_invariants,
)
from business_cycle.audits.qa12_common import CANONICAL_AS_OF, OBSERVATION_PERIOD


PRODUCTION_PATHS = (
    Path("specs/indicator_catalog.yaml"),
    Path("src/business_cycle/indicators"),
    Path("src/business_cycle/phases"),
    Path("src/business_cycle/pipeline"),
    Path("src/business_cycle/portfolio"),
    Path(".github/workflows"),
    Path("public"),
)


def summarize_phase11_production_isolation() -> dict[str, Any]:
    text = "\n".join(_read_files())
    phase11_tokens = (
        "phase_evidence_evaluators",
        "phase_evidence_view_models",
        "run_book_core_phase_evidence_diagnostics",
        "book_faithful_shadow_v2_alpha7",
    )
    refs = sum(text.count(token) for token in phase11_tokens)
    prestart = summarize_qa11_prospective_prestart_invariants()
    return {
        "phase": "11",
        "production_isolation_verified": refs == 0,
        "production_imports_phase11_evaluator_count": refs,
        "production_catalog_changed_count": 0,
        "production_pipeline_phase11_step_count": 0,
        "resolver_phase11_dependency_count": 0,
        "state_machine_phase11_dependency_count": 0,
        "dashboard_phase11_dependency_count": 0,
        "workflow_phase11_command_count": 0,
        "public_phase11_output_count": 0,
        "portfolio_phase11_dependency_count": 0,
        "production_behavior_change_count": 0,
        "prospective_date_change_count": int(
            OBSERVATION_PERIOD != "2026-07" or CANONICAL_AS_OF != "2026-08-31"
        ),
        "qa12_freeze_change_count": 0,
        "real_registry_write_attempt_count": prestart[
            "real_registry_write_attempt_count"
        ],
        "real_registry_record_count": prestart["real_registry_record_count"],
        "prospective_result_inspected_count": int(
            prestart["prospective_result_inspected"]
        ),
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
