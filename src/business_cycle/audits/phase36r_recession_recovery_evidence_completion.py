"""Phase 36R recession/recovery evidence completion audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.post_evidence_completion_validation_rerun import (
    summarize_post_evidence_completion_validation_rerun,
)
from business_cycle.validation.recession_recovery_evidence_completion import (
    summarize_recession_recovery_evidence_completion,
)


DEFAULT_PHASE36R_AUDIT_PATH = Path(
    "specs/audits/phase36r_recession_recovery_evidence_completion.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase36r_recession_recovery_evidence_completion(
    path: str | Path = DEFAULT_PHASE36R_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    completion = summarize_recession_recovery_evidence_completion()
    rerun = summarize_post_evidence_completion_validation_rerun()
    summary = {
        "phase": "36R",
        "phase_id": "36R",
        "recession_recovery_evidence_completion_runtime_ready": completion[
            "recession_recovery_evidence_completion_runtime_ready"
        ],
        "post_evidence_completion_validation_rerun_ready": rerun[
            "post_evidence_completion_validation_rerun_ready"
        ],
        **{
            key: completion[key]
            for key in (
                "attempted_fix_iteration_count",
                "scenario_count",
                "target_recession_recovery_scenario_count",
                "pre_comparable_scenario_count",
                "post_comparable_scenario_count",
                "phase_evidence_completion_attempted_scenario_count",
                "safe_fixable_recession_recovery_gap_count",
                "unresolved_safe_fixable_recession_recovery_gap_count",
                "evidence_completion_false_positive_count",
                "false_comparability_count",
                "scenario_promoted_without_required_evidence_count",
                "scenario_promoted_by_taxonomy_only_count",
                "scenario_promoted_by_modern_proxy_count",
                "evidence_rule_semantics_modified_count",
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
                "metric_computation_scope",
                "economic_performance_metric_count",
                "backtest_execution_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
                "phase36r_progress_status",
                "development_next_phase",
                "target_recession_recovery_scenario_ids",
                "newly_comparable_scenario_ids",
                "remaining_non_comparable_scenario_ids",
                "role_level_remaining_evidence_gaps",
            )
        },
        "completion": completion,
        "rerun": rerun,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    preferred_stop = (
        summary["post_comparable_scenario_count"]
        > summary["pre_comparable_scenario_count"]
    )
    acceptable_stop = (
        summary["post_comparable_scenario_count"] == 2
        and summary["attempted_fix_iteration_count"] >= 2
        and summary["safe_fixable_recession_recovery_gap_count"] == 0
        and summary["unresolved_safe_fixable_recession_recovery_gap_count"] == 0
    )
    return (
        (preferred_stop or acceptable_stop)
        and summary["recession_recovery_evidence_completion_runtime_ready"] is True
        and summary["post_evidence_completion_validation_rerun_ready"] is True
        and summary["post_comparable_scenario_count"] >= 2
        and summary["false_comparability_count"] == 0
        and summary["evidence_completion_false_positive_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase36r_recession_recovery_evidence_completion"
    ]["expected"]
