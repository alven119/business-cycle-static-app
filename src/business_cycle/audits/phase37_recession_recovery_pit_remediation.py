"""Phase 37 recession/recovery point-in-time remediation audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.controlled_pit_backfill import (
    summarize_controlled_pit_backfill,
)
from business_cycle.validation.post_pit_remediation_validation_rerun import (
    summarize_post_pit_remediation_validation_rerun,
)
from business_cycle.validation.recession_recovery_pit_gap_matrix import (
    summarize_recession_recovery_pit_gap_matrix,
)
from business_cycle.validation.recession_recovery_pit_remediation import (
    summarize_recession_recovery_pit_remediation,
)


DEFAULT_PHASE37_AUDIT_PATH = Path(
    "specs/audits/phase37_recession_recovery_pit_remediation.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase37_recession_recovery_pit_remediation(
    path: str | Path = DEFAULT_PHASE37_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    matrix = summarize_recession_recovery_pit_gap_matrix()
    remediation = summarize_recession_recovery_pit_remediation()
    backfill = summarize_controlled_pit_backfill()
    rerun = summarize_post_pit_remediation_validation_rerun()
    summary = {
        "phase": "37",
        "phase_id": 37,
        "recession_recovery_pit_gap_matrix_ready": matrix[
            "recession_recovery_pit_gap_matrix_ready"
        ],
        "recession_recovery_pit_remediation_runtime_ready": remediation[
            "recession_recovery_pit_remediation_runtime_ready"
        ],
        "controlled_pit_backfill_ready": backfill["controlled_pit_backfill_ready"],
        "post_pit_remediation_validation_rerun_ready": rerun[
            "post_pit_remediation_validation_rerun_ready"
        ],
        **{
            key: remediation[key]
            for key in (
                "attempted_fix_iteration_count",
                "scenario_count",
                "target_recession_recovery_scenario_count",
                "pre_insufficient_point_in_time_role_gap_count",
                "post_insufficient_point_in_time_role_gap_count",
                "safe_fixable_pit_gap_count",
                "unresolved_safe_fixable_pit_gap_count",
                "official_history_insufficient_gap_count",
                "genuine_source_unavailable_gap_count",
                "rule_unresolved_gap_count",
                "revised_fallback_used_count",
                "proxy_fallback_used_count",
                "secret_logged_count",
                "raw_data_committed_count",
                "pre_comparable_scenario_count",
                "post_comparable_scenario_count",
                "newly_comparable_scenario_ids",
                "remaining_non_comparable_scenario_ids",
                "false_comparability_count",
                "scenario_promoted_without_required_evidence_count",
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
                "phase37_progress_status",
                "development_next_phase",
            )
        },
        "cache_remediated_pit_role_gap_count": matrix[
            "cache_remediated_pit_role_gap_count"
        ],
        "cache_remediated_pit_role_ids": matrix["cache_remediated_pit_role_ids"],
        "pre_insufficient_point_in_time_scenario_role_gap_count": matrix[
            "pre_insufficient_point_in_time_scenario_role_gap_count"
        ],
        "post_insufficient_point_in_time_scenario_role_gap_count": matrix[
            "post_insufficient_point_in_time_scenario_role_gap_count"
        ],
        "backfill_requested_series_count": backfill[
            "backfill_requested_series_count"
        ],
        "backfill_executed_series_count": backfill["backfill_executed_series_count"],
        "backfill_blocked_series_count": backfill["backfill_blocked_series_count"],
        "network_attempted": backfill["network_attempted"],
        "cache_write_attempted": backfill["cache_write_attempted"],
        "updated_historical_accuracy_metric_count": rerun[
            "updated_historical_accuracy_metric_count"
        ],
        "updated_scenario_trace_count": rerun["updated_scenario_trace_count"],
        "updated_blockage_diagnostic_scenario_count": rerun[
            "updated_blockage_diagnostic_scenario_count"
        ],
        "historical_validation_result_artifact_count": rerun[
            "historical_validation_result_artifact_count"
        ],
        "matrix": matrix,
        "remediation": remediation,
        "backfill": backfill,
        "rerun": rerun,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["post_insufficient_point_in_time_role_gap_count"]
        < summary["pre_insufficient_point_in_time_role_gap_count"]
        and summary["attempted_fix_iteration_count"] >= 2
        and summary["safe_fixable_pit_gap_count"] == 0
        and summary["unresolved_safe_fixable_pit_gap_count"] == 0
        and summary["false_comparability_count"] == 0
        and summary["network_attempted"] is False
        and summary["cache_write_attempted"] is False
        and summary["matrix"]["recession_recovery_pit_gap_matrix_ready"] is True
        and summary["remediation"]["recession_recovery_pit_remediation_runtime_ready"]
        is True
        and summary["backfill"]["controlled_pit_backfill_ready"] is True
        and summary["rerun"]["post_pit_remediation_validation_rerun_ready"] is True
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase37_recession_recovery_pit_remediation"
    ]["expected"]
