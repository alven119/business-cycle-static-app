"""Phase 36 historical validation result realization audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_validation_results import (
    summarize_historical_validation_results,
)
from business_cycle.validation.post_validation_result_rerun import (
    summarize_post_validation_result_rerun,
)
from business_cycle.validation.recession_recovery_comparability_unblock import (
    summarize_recession_recovery_comparability_unblock,
)


DEFAULT_PHASE36_AUDIT_PATH = Path(
    "specs/audits/phase36_historical_validation_result_realization.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase36_historical_validation_result_realization(
    path: str | Path = DEFAULT_PHASE36_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    unblock = summarize_recession_recovery_comparability_unblock()
    result = summarize_historical_validation_results()
    rerun = summarize_post_validation_result_rerun()
    development_next_phase: int | str = (
        37
        if unblock["post_comparable_scenario_count"]
        > unblock["pre_comparable_scenario_count"]
        else "PHASE_36_REVIEW"
    )
    summary = {
        "phase": "36",
        "phase_id": 36,
        "historical_validation_result_runtime_ready": result[
            "historical_validation_result_runtime_ready"
        ],
        "recession_recovery_comparability_unblock_ready": unblock[
            "recession_recovery_comparability_unblock_ready"
        ],
        "post_validation_result_rerun_ready": rerun[
            "post_validation_result_rerun_ready"
        ],
        "attempted_fix_iteration_count": unblock[
            "attempted_fix_iteration_count"
        ],
        "scenario_count": unblock["scenario_count"],
        "pre_comparable_scenario_count": unblock[
            "pre_comparable_scenario_count"
        ],
        "post_comparable_scenario_count": unblock[
            "post_comparable_scenario_count"
        ],
        "comparable_scenario_count": result["comparable_scenario_count"],
        "historical_validation_result_artifact_count": result[
            "historical_validation_result_artifact_count"
        ],
        **{
            key: unblock[key]
            for key in (
                "safe_fixable_recession_recovery_gap_count",
                "unresolved_safe_fixable_recession_recovery_gap_count",
                "all_remaining_recession_recovery_non_comparable_reasons_are_genuine",
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
                "metric_computation_scope",
                "economic_performance_metric_count",
                "backtest_execution_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
                "phase36_validation_progress_status",
            )
        },
        "remaining_non_comparable_evidence": unblock[
            "recession_recovery_unblock_artifact"
        ]["remaining_recession_recovery_non_comparable_evidence"],
        "comparable_scenario_ids": [
            item["scenario_id"]
            for item in result["historical_validation_result_artifact"][
                "comparable_scenario_results"
            ]
        ],
        "recession_recovery_scenario_profiles": unblock[
            "recession_recovery_unblock_artifact"
        ]["recession_recovery_scenario_profiles"],
        "historical_validation_result_artifact": result[
            "historical_validation_result_artifact"
        ],
        "development_next_phase": development_next_phase,
        "unblock": unblock,
        "result_run": result,
        "rerun": rerun,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    acceptable_stop = (
        summary["post_comparable_scenario_count"] == 2
        and summary["attempted_fix_iteration_count"] >= 2
        and summary[
            "all_remaining_recession_recovery_non_comparable_reasons_are_genuine"
        ]
        is True
    )
    preferred_stop = (
        summary["post_comparable_scenario_count"]
        > summary["pre_comparable_scenario_count"]
    )
    return (
        (preferred_stop or acceptable_stop)
        and summary["historical_validation_result_runtime_ready"] is True
        and summary["recession_recovery_comparability_unblock_ready"] is True
        and summary["post_validation_result_rerun_ready"] is True
        and summary["comparable_scenario_count"]
        == summary["post_comparable_scenario_count"]
        and summary["historical_validation_result_artifact_count"] > 0
        and summary["safe_fixable_recession_recovery_gap_count"] == 0
        and summary["unresolved_safe_fixable_recession_recovery_gap_count"] == 0
        and summary["false_comparability_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase36_historical_validation_result_realization"
    ]["expected"]
