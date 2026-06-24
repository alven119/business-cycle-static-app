"""Phase 29 historical accuracy metric readiness audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase28_predicted_label_comparison_closure import (
    summarize_phase28_predicted_label_comparison_closure,
)
from business_cycle.validation.historical_accuracy_metrics import (
    summarize_historical_accuracy_metrics,
)


DEFAULT_HISTORICAL_ACCURACY_METRIC_READINESS_PATH = Path(
    "specs/audits/historical_accuracy_metric_readiness.yaml"
)


def summarize_historical_accuracy_metric_readiness(
    path: str | Path = DEFAULT_HISTORICAL_ACCURACY_METRIC_READINESS_PATH,
) -> dict[str, Any]:
    spec = _load_spec(path)
    expected = spec["expected_counters"]
    metrics = summarize_historical_accuracy_metrics()
    phase28 = summarize_phase28_predicted_label_comparison_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "29",
        "readiness_id": spec["readiness_id"],
        "readiness_version": spec["readiness_version"],
        "historical_accuracy_metric_artifact_contract_ready": metrics[
            "historical_accuracy_metric_artifact_contract_ready"
        ],
        "historical_accuracy_metric_runtime_ready": metrics[
            "historical_accuracy_metric_runtime_ready"
        ],
        "preregistered_metric_registry_used": metrics[
            "preregistered_metric_registry_used"
        ],
        "scenario_count": metrics["scenario_count"],
        "label_comparison_artifact_count": metrics[
            "label_comparison_artifact_count"
        ],
        "comparable_scenario_count": metrics["comparable_scenario_count"],
        "non_comparable_scenario_count": metrics["non_comparable_scenario_count"],
        "abstained_scenario_count": metrics["abstained_scenario_count"],
        "blocked_scenario_count": metrics["blocked_scenario_count"],
        "taxonomy_mismatch_count": metrics["taxonomy_mismatch_count"],
        "historical_accuracy_metric_count": metrics[
            "historical_accuracy_metric_count"
        ],
        "computed_metric_count": metrics["computed_metric_count"],
        "skipped_metric_count": metrics["skipped_metric_count"],
        "economic_performance_metric_count": metrics[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": metrics["metric_computation_enabled"],
        "metric_computation_scope": metrics["metric_computation_scope"],
        "backtest_execution_enabled": metrics["backtest_execution_enabled"],
        "label_used_by_runtime_count": metrics["label_used_by_runtime_count"],
        "mapping_rule_modified_after_comparison_count": metrics[
            "mapping_rule_modified_after_comparison_count"
        ],
        "threshold_modified_after_metric_count": metrics[
            "threshold_modified_after_metric_count"
        ],
        "numeric_weight_added_count": metrics["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": metrics[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": metrics["role_count_voting_added_count"],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "candidate_phase_emitted": metrics["candidate_phase_emitted"],
        "current_phase_emitted": metrics["current_phase_emitted"],
        "prohibited_metric_field_count": metrics["prohibited_metric_field_count"],
        "production_behavior_change_count": metrics[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": metrics[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": metrics[
            "real_registry_write_attempt_count"
        ],
        "forbidden_repo_output_count": metrics["forbidden_repo_output_count"],
        "missing_comparison_artifact_count": metrics[
            "missing_comparison_artifact_count"
        ],
        "malformed_comparison_artifact_count": metrics[
            "malformed_comparison_artifact_count"
        ],
        "forbidden_comparison_artifact_field_count": metrics[
            "forbidden_comparison_artifact_field_count"
        ],
        "duplicate_scenario_artifact_count": metrics[
            "duplicate_scenario_artifact_count"
        ],
        "registry_hash_mismatch_count": metrics["registry_hash_mismatch_count"],
        "metric_run": metrics,
        "phase28_closure": phase28,
        "leakage": leakage,
    }
    summary["historical_accuracy_metric_readiness_ready"] = _matches_expected(
        summary,
        expected,
    )
    return summary


def _matches_expected(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "historical_accuracy_metric_readiness_ready":
            continue
        if key == "historical_accuracy_metric_count_minimum":
            if summary["historical_accuracy_metric_count"] < value:
                return False
            continue
        if summary.get(key) != value:
            return False
    return (
        summary["phase28_closure"]["result"] == "passed"
        and summary["phase28_closure"]["label_comparison_executed"] is True
        and summary["phase28_closure"]["historical_accuracy_metric_count"] == 0
        and summary["missing_comparison_artifact_count"] == 0
        and summary["malformed_comparison_artifact_count"] == 0
        and summary["forbidden_comparison_artifact_field_count"] == 0
        and summary["duplicate_scenario_artifact_count"] == 0
        and summary["registry_hash_mismatch_count"] == 0
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_spec(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "historical_accuracy_metric_readiness"
    ]
