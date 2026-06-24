"""Phase 33 genuine blocker resolution execution audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.genuine_blocker_resolution_execution import (
    summarize_genuine_blocker_resolution_execution,
)
from business_cycle.validation.post_resolution_validation_rerun import (
    summarize_post_resolution_validation_rerun,
)


DEFAULT_PHASE33_EXECUTION_AUDIT_PATH = Path(
    "specs/audits/phase33_genuine_blocker_resolution_execution.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase33_genuine_blocker_resolution_execution(
    path: str | Path = DEFAULT_PHASE33_EXECUTION_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    execution = summarize_genuine_blocker_resolution_execution()
    rerun = summarize_post_resolution_validation_rerun()
    summary = {
        "phase": "33",
        "genuine_blocker_resolution_execution_ready": execution[
            "genuine_blocker_resolution_execution_ready"
        ],
        "post_resolution_validation_rerun_ready": rerun[
            "post_resolution_validation_rerun_ready"
        ],
        **{
            key: execution[key]
            for key in (
                "work_package_count",
                "safe_executable_work_package_count",
                "executed_work_package_count",
                "still_genuine_blocked_work_package_count",
                "work_package_without_execution_reason_count",
                "pre_resolution_blocked_scenario_count",
                "post_resolution_blocked_scenario_count",
                "pre_resolution_comparable_scenario_count",
                "post_resolution_comparable_scenario_count",
                "false_resolution_count",
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
                "phase33_resolution_progress_status",
            )
        },
        "updated_predicted_label_artifact_count": rerun[
            "updated_predicted_label_artifact_count"
        ],
        "updated_comparison_artifact_count": rerun[
            "updated_comparison_artifact_count"
        ],
        "updated_historical_accuracy_metric_count": rerun[
            "updated_historical_accuracy_metric_count"
        ],
        "updated_blockage_diagnostic_scenario_count": rerun[
            "updated_blockage_diagnostic_scenario_count"
        ],
        "updated_scenario_trace_count": rerun["updated_scenario_trace_count"],
        "execution": execution,
        "rerun": rerun,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        summary["genuine_blocker_resolution_execution_ready"]
        == expected["genuine_blocker_resolution_execution_ready"]
        and summary["post_resolution_validation_rerun_ready"]
        == expected["post_resolution_validation_rerun_ready"]
        and summary["work_package_count"] == expected["work_package_count"]
        and (
            summary["executed_work_package_count"]
            == summary["safe_executable_work_package_count"]
        )
        is expected["executed_work_package_count_matches_safe_count"]
        and summary["work_package_without_execution_reason_count"]
        == expected["work_package_without_execution_reason_count"]
        and summary["pre_resolution_blocked_scenario_count"]
        == expected["pre_resolution_blocked_scenario_count"]
        and summary["post_resolution_blocked_scenario_count"]
        <= expected["max_post_resolution_blocked_scenario_count"]
        and all(
            summary[key] == value
            for key, value in expected.items()
            if key
            not in {
                "genuine_blocker_resolution_execution_ready",
                "post_resolution_validation_rerun_ready",
                "work_package_count",
                "executed_work_package_count_matches_safe_count",
                "max_post_resolution_blocked_scenario_count",
            }
        )
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase33_genuine_blocker_resolution_execution"
    ]["expected"]
