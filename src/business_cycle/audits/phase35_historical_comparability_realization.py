"""Phase 35 historical comparability realization audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.autonomous_comparability_realization import (
    summarize_autonomous_comparability_realization,
)
from business_cycle.validation.historical_comparability_diagnostics import (
    summarize_historical_comparability_diagnostics,
)
from business_cycle.validation.post_comparability_validation_rerun import (
    summarize_post_comparability_validation_rerun,
)


DEFAULT_PHASE35_AUDIT_PATH = Path(
    "specs/audits/phase35_historical_comparability_realization.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase35_historical_comparability_realization(
    path: str | Path = DEFAULT_PHASE35_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    runtime = summarize_autonomous_comparability_realization()
    rerun = summarize_post_comparability_validation_rerun()
    diagnostics = summarize_historical_comparability_diagnostics()
    summary = {
        "phase": "35",
        "phase_id": 35,
        **{
            key: runtime[key]
            for key in (
                "autonomous_comparability_realization_ready",
                "attempted_fix_iteration_count",
                "scenario_count",
                "pre_blocked_scenario_count",
                "post_blocked_scenario_count",
                "pre_comparable_scenario_count",
                "post_comparable_scenario_count",
                "safe_fixable_comparability_gap_count",
                "unresolved_safe_fixable_comparability_gap_count",
                "all_remaining_non_comparable_reasons_are_genuine",
                "non_comparable_without_attempted_fix_or_genuine_evidence_count",
                "false_comparability_count",
                "scenario_promoted_without_required_evidence_count",
                "scenario_promoted_by_taxonomy_only_count",
                "scenario_promoted_by_modern_proxy_count",
                "evidence_rule_modified_count",
                "predicted_mapping_rule_modified_count",
                "formal_decision_contract_modified_count",
                "threshold_modified_count",
                "numeric_weight_added_count",
                "arbitrary_threshold_added_count",
                "role_count_voting_added_count",
                "historical_tuning_leakage_count",
                "label_used_by_runtime_count",
                "historical_accuracy_metric_count",
                "new_accuracy_metric_computed_count",
                "economic_performance_metric_count",
                "metric_computation_scope",
                "backtest_execution_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
                "phase35_comparability_progress_status",
            )
        },
        "post_comparability_validation_rerun_ready": rerun[
            "post_comparability_validation_rerun_ready"
        ],
        "historical_comparability_diagnostics_ready": diagnostics[
            "historical_comparability_diagnostics_ready"
        ],
        "remaining_non_comparable_evidence": runtime[
            "autonomous_comparability_realization_artifact"
        ]["remaining_non_comparable_evidence"],
        "scenario_comparability_profiles": runtime[
            "autonomous_comparability_realization_artifact"
        ]["scenario_comparability_profiles"],
        "runtime": runtime,
        "rerun": rerun,
        "diagnostics": diagnostics,
    }
    summary["development_next_phase"] = (
        36
        if summary["post_comparable_scenario_count"]
        > summary["pre_comparable_scenario_count"]
        else "PHASE_35_REVIEW"
    )
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["post_comparable_scenario_count"]
        > summary["pre_comparable_scenario_count"]
        and summary["post_blocked_scenario_count"] == 0
        and summary["runtime"]["autonomous_comparability_realization_ready"] is True
        and summary["rerun"]["post_comparability_validation_rerun_ready"] is True
        and summary["diagnostics"]["historical_comparability_diagnostics_ready"]
        is True
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase35_historical_comparability_realization"
    ]["expected"]
