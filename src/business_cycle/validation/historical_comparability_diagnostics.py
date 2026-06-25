"""Phase 35 historical comparability diagnostics."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.validation.autonomous_comparability_realization import (
    build_autonomous_comparability_realization,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase35_historical_comparability_diagnostics_v1"
GENERATED_AT_UTC = "2026-06-25T00:00:00Z"


@lru_cache(maxsize=1)
def build_historical_comparability_diagnostics() -> dict[str, Any]:
    comparability = build_autonomous_comparability_realization()
    artifact = comparability["autonomous_comparability_realization_artifact"]
    profiles = artifact["scenario_comparability_profiles"]
    status_counter = Counter(profile["post_comparison_status"] for profile in profiles)
    gap_counter = Counter(profile["comparability_gap_class"] for profile in profiles)
    diagnostics_artifact = {
        "artifact_version": "phase35_historical_comparability_diagnostics_v1",
        "diagnostic_run_id": RUN_ID,
        "source_comparability_run_id": comparability["run_id"],
        "scenario_count": comparability["scenario_count"],
        "pre_blocked_scenario_count": comparability["pre_blocked_scenario_count"],
        "post_blocked_scenario_count": comparability["post_blocked_scenario_count"],
        "pre_comparable_scenario_count": comparability[
            "pre_comparable_scenario_count"
        ],
        "post_comparable_scenario_count": comparability[
            "post_comparable_scenario_count"
        ],
        "post_comparison_status_summary": dict(sorted(status_counter.items())),
        "comparability_gap_summary": dict(sorted(gap_counter.items())),
        "scenario_comparability_profiles": profiles,
        "remaining_non_comparable_evidence": artifact[
            "remaining_non_comparable_evidence"
        ],
        "false_comparability_count": comparability["false_comparability_count"],
        "scenario_promoted_without_required_evidence_count": comparability[
            "scenario_promoted_without_required_evidence_count"
        ],
        "scenario_promoted_by_taxonomy_only_count": comparability[
            "scenario_promoted_by_taxonomy_only_count"
        ],
        "scenario_promoted_by_modern_proxy_count": comparability[
            "scenario_promoted_by_modern_proxy_count"
        ],
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "runtime_decision_logic",
            "production_dashboard_output",
            "portfolio_or_trade_decision",
        ],
        "provenance": {
            "label_used_by_runtime_count": 0,
            "evidence_rule_modified_count": 0,
            "predicted_mapping_rule_modified_count": 0,
            "threshold_modified_count": 0,
            "new_accuracy_metric_computed_count": 0,
            "economic_performance_metric_count": 0,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
        },
    }
    ready = (
        comparability["autonomous_comparability_realization_ready"] is True
        and diagnostics_artifact["scenario_count"] == 5
        and diagnostics_artifact["pre_blocked_scenario_count"] == 0
        and diagnostics_artifact["post_blocked_scenario_count"] == 0
        and diagnostics_artifact["post_comparable_scenario_count"]
        > diagnostics_artifact["pre_comparable_scenario_count"]
        and diagnostics_artifact["false_comparability_count"] == 0
    )
    return {
        "phase": "35",
        "run_id": RUN_ID,
        "historical_comparability_diagnostics_ready": ready,
        "scenario_count": diagnostics_artifact["scenario_count"],
        "pre_blocked_scenario_count": diagnostics_artifact[
            "pre_blocked_scenario_count"
        ],
        "post_blocked_scenario_count": diagnostics_artifact[
            "post_blocked_scenario_count"
        ],
        "pre_comparable_scenario_count": diagnostics_artifact[
            "pre_comparable_scenario_count"
        ],
        "post_comparable_scenario_count": diagnostics_artifact[
            "post_comparable_scenario_count"
        ],
        "remaining_non_comparable_scenario_count": len(
            diagnostics_artifact["remaining_non_comparable_evidence"]
        ),
        "false_comparability_count": diagnostics_artifact[
            "false_comparability_count"
        ],
        "scenario_promoted_without_required_evidence_count": diagnostics_artifact[
            "scenario_promoted_without_required_evidence_count"
        ],
        "scenario_promoted_by_taxonomy_only_count": diagnostics_artifact[
            "scenario_promoted_by_taxonomy_only_count"
        ],
        "scenario_promoted_by_modern_proxy_count": diagnostics_artifact[
            "scenario_promoted_by_modern_proxy_count"
        ],
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": comparability[
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "forbidden_repo_output_count": 0,
        "historical_comparability_diagnostics_artifact": diagnostics_artifact,
        "comparability_run": comparability,
    }


def summarize_historical_comparability_diagnostics() -> dict[str, Any]:
    run = build_historical_comparability_diagnostics()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "historical_comparability_diagnostics_ready",
            "scenario_count",
            "pre_blocked_scenario_count",
            "post_blocked_scenario_count",
            "pre_comparable_scenario_count",
            "post_comparable_scenario_count",
            "remaining_non_comparable_scenario_count",
            "false_comparability_count",
            "scenario_promoted_without_required_evidence_count",
            "scenario_promoted_by_taxonomy_only_count",
            "scenario_promoted_by_modern_proxy_count",
            "label_used_by_runtime_count",
            "historical_accuracy_metric_count",
            "new_accuracy_metric_computed_count",
            "economic_performance_metric_count",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "forbidden_repo_output_count",
            "historical_comparability_diagnostics_artifact",
        )
    }


def write_historical_comparability_diagnostics(
    diagnostic_run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": diagnostic_run["run_id"],
        "phase": diagnostic_run["phase"],
        "historical_comparability_diagnostics_artifact": diagnostic_run[
            "historical_comparability_diagnostics_artifact"
        ],
        "scenario_count": diagnostic_run["scenario_count"],
        "pre_comparable_scenario_count": diagnostic_run[
            "pre_comparable_scenario_count"
        ],
        "post_comparable_scenario_count": diagnostic_run[
            "post_comparable_scenario_count"
        ],
        "false_comparability_count": diagnostic_run["false_comparability_count"],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "historical_comparability_diagnostics_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 35 comparability diagnostics output must be under /tmp: {output}"
        )
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved
