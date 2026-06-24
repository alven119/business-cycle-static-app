"""Phase 28 predicted-label comparison readiness audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.predicted_label_comparison_artifacts import (
    summarize_predicted_label_comparison_artifacts,
)


DEFAULT_PREDICTED_LABEL_COMPARISON_READINESS_PATH = Path(
    "specs/audits/predicted_label_comparison_readiness.yaml"
)


def load_predicted_label_comparison_readiness(
    path: str | Path = DEFAULT_PREDICTED_LABEL_COMPARISON_READINESS_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("predicted label comparison readiness must map")
    readiness = payload.get("predicted_label_comparison_readiness")
    if not isinstance(readiness, dict):
        raise ValueError("predicted_label_comparison_readiness must be a mapping")
    return readiness


def summarize_predicted_label_comparison_readiness(
    path: str | Path = DEFAULT_PREDICTED_LABEL_COMPARISON_READINESS_PATH,
) -> dict[str, Any]:
    readiness = load_predicted_label_comparison_readiness(path)
    comparison_summary = summarize_predicted_label_comparison_artifacts()
    expected = readiness["expected_counters"]
    storage = readiness["storage_policy"]
    prohibited_runtime = readiness["prohibited_runtime_usage"]
    expected_without_self = {
        key: value
        for key, value in expected.items()
        if key != "predicted_label_comparison_readiness_ready"
    }
    ready = (
        readiness["readiness_status"]
        == "ready_comparison_artifacts_no_accuracy_or_performance_metrics"
        and comparison_summary[
            "predicted_label_comparison_artifact_contract_ready"
        ]
        is True
        and comparison_summary["predicted_label_comparison_generator_ready"] is True
        and all(
            comparison_summary[key] == value
            for key, value in expected_without_self.items()
        )
        and storage["tmp_comparison_artifacts_allowed"] is True
        and storage["committed_comparison_artifacts_allowed"] is False
        and storage["data_backtests_write_allowed"] is False
        and storage["data_prospective_write_allowed"] is False
        and storage["public_output_allowed"] is False
        and prohibited_runtime["label_runtime_usage_allowed"] is False
        and prohibited_runtime["label_comparison_can_tune_mapping"] is False
        and prohibited_runtime["metric_computation_allowed"] is False
        and prohibited_runtime["backtest_execution_allowed"] is False
        and prohibited_runtime["formal_decision_model_enabled"] is False
        and prohibited_runtime["candidate_model_enabled"] is False
        and prohibited_runtime["production_integration_allowed"] is False
    )
    return {
        "phase": "28",
        "readiness_id": readiness["readiness_id"],
        "readiness_version": readiness["readiness_version"],
        "predicted_label_comparison_artifact_contract_ready": comparison_summary[
            "predicted_label_comparison_artifact_contract_ready"
        ],
        "predicted_label_comparison_generator_ready": comparison_summary[
            "predicted_label_comparison_generator_ready"
        ],
        "predicted_label_comparison_readiness_ready": ready,
        **{key: comparison_summary[key] for key in expected_without_self},
        "numeric_weight_added_count": comparison_summary["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": comparison_summary[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": comparison_summary[
            "role_count_voting_added_count"
        ],
        "historical_tuning_leakage_count": comparison_summary[
            "historical_tuning_leakage_count"
        ],
        "tmp_comparison_artifacts_allowed": storage[
            "tmp_comparison_artifacts_allowed"
        ],
        "committed_comparison_artifacts_allowed": storage[
            "committed_comparison_artifacts_allowed"
        ],
        "data_backtests_write_allowed": storage["data_backtests_write_allowed"],
        "data_prospective_write_allowed": storage[
            "data_prospective_write_allowed"
        ],
        "public_output_allowed": storage["public_output_allowed"],
        "comparison_summary": comparison_summary,
        "readiness": readiness,
    }
