"""Phase 21 historical metric preregistration readiness audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.validation.historical_label_comparison_contract import (
    summarize_historical_label_comparison_contract,
)
from business_cycle.validation.historical_metric_preregistration import (
    summarize_historical_metric_preregistration,
)


DEFAULT_HISTORICAL_METRIC_READINESS_PATH = Path(
    "specs/audits/historical_metric_readiness.yaml"
)


def summarize_historical_metric_readiness(
    path: str | Path = DEFAULT_HISTORICAL_METRIC_READINESS_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    label_contract = summarize_historical_label_comparison_contract()
    preregistration = summarize_historical_metric_preregistration()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    leakage = summarize_phase11_evidence_rule_leakage()
    historical_tuning_leakage_count = _sum_int_counts(leakage)
    summary = {
        "phase": "21",
        "historical_label_comparison_contract_ready": label_contract[
            "historical_label_comparison_contract_ready"
        ],
        "historical_metric_preregistration_ready": preregistration[
            "historical_metric_preregistration_ready"
        ],
        "historical_metric_registry_ready": preregistration[
            "historical_metric_registry_ready"
        ],
        "preregistered_metric_count": preregistration[
            "preregistered_metric_count"
        ],
        "label_runtime_usage_prohibited": label_contract[
            "label_runtime_usage_prohibited"
        ],
        "label_comparison_executed": preregistration[
            "label_comparison_executed"
        ],
        "historical_accuracy_metric_count": preregistration[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": preregistration[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": preregistration[
            "metric_computation_enabled"
        ],
        "backtest_execution_enabled": preregistration[
            "backtest_execution_enabled"
        ],
        "holdout_registered": preregistration["holdout_registered"],
        "candidate_selection_enabled": preregistration[
            "candidate_selection_enabled"
        ],
        "candidate_phase_emitted": preregistration["candidate_phase_emitted"],
        "current_phase_emitted": preregistration["current_phase_emitted"],
        "production_behavior_change_count": label_contract[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": label_contract[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": label_contract[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": preregistration[
            "numeric_weight_added_count"
        ],
        "arbitrary_threshold_added_count": preregistration[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": preregistration[
            "role_count_voting_added_count"
        ],
        "historical_tuning_leakage_count": historical_tuning_leakage_count,
        "label_comparison_contract": label_contract,
        "metric_preregistration": preregistration,
        "qa12_closure": qa12,
        "leakage": leakage,
    }
    summary["metric_readiness_ready"] = _matches_expected(summary, expected)
    return summary


def _matches_expected(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["qa12_closure"]["result"] == "passed"
        and summary["qa12_closure"]["real_registry_record_count"] == 0
        and summary["qa12_closure"]["real_registry_write_attempt_count"] == 0
        and summary["qa12_closure"]["prospective_protocol_started"] is False
    )


def _sum_int_counts(payload: dict[str, Any]) -> int:
    return sum(
        value
        for key, value in payload.items()
        if key.endswith("_count") and type(value) is int
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "historical_metric_readiness"
    ]["expected"]
