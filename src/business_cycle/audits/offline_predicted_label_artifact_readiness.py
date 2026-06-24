"""Phase 27 offline predicted-label artifact readiness audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.offline_predicted_label_artifacts import (
    summarize_offline_predicted_label_artifacts,
)


DEFAULT_OFFLINE_PREDICTED_LABEL_ARTIFACT_READINESS_PATH = Path(
    "specs/audits/offline_predicted_label_artifact_readiness.yaml"
)


def load_offline_predicted_label_artifact_readiness(
    path: str | Path = DEFAULT_OFFLINE_PREDICTED_LABEL_ARTIFACT_READINESS_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("offline predicted label artifact readiness must map")
    readiness = payload.get("offline_predicted_label_artifact_readiness")
    if not isinstance(readiness, dict):
        raise ValueError(
            "offline_predicted_label_artifact_readiness must be a mapping"
        )
    return readiness


def summarize_offline_predicted_label_artifact_readiness(
    path: str | Path = DEFAULT_OFFLINE_PREDICTED_LABEL_ARTIFACT_READINESS_PATH,
) -> dict[str, Any]:
    readiness = load_offline_predicted_label_artifact_readiness(path)
    artifact_summary = summarize_offline_predicted_label_artifacts()
    expected = readiness["expected_counters"]
    storage = readiness["storage_policy"]
    prohibited_runtime = readiness["prohibited_runtime_usage"]
    expected_without_self = {
        key: value
        for key, value in expected.items()
        if key != "offline_predicted_label_artifact_readiness_ready"
    }
    ready = (
        readiness["readiness_status"]
        == "ready_predicted_label_artifacts_no_comparison_or_metrics"
        and artifact_summary["offline_predicted_label_artifact_contract_ready"] is True
        and artifact_summary["offline_predicted_label_artifact_generator_ready"] is True
        and all(
            artifact_summary[key] == value
            for key, value in expected_without_self.items()
        )
        and storage["tmp_predicted_label_artifacts_allowed"] is True
        and storage["committed_predicted_label_artifacts_allowed"] is False
        and storage["data_backtests_write_allowed"] is False
        and storage["data_prospective_write_allowed"] is False
        and storage["public_output_allowed"] is False
        and prohibited_runtime["label_runtime_usage_allowed"] is False
        and prohibited_runtime["label_comparison_execution_allowed"] is False
        and prohibited_runtime["metric_computation_allowed"] is False
        and prohibited_runtime["backtest_execution_allowed"] is False
        and prohibited_runtime["formal_decision_model_enabled"] is False
        and prohibited_runtime["candidate_model_enabled"] is False
        and prohibited_runtime["production_integration_allowed"] is False
    )
    return {
        "phase": "27",
        "readiness_id": readiness["readiness_id"],
        "readiness_version": readiness["readiness_version"],
        "offline_predicted_label_artifact_contract_ready": artifact_summary[
            "offline_predicted_label_artifact_contract_ready"
        ],
        "offline_predicted_label_artifact_generator_ready": artifact_summary[
            "offline_predicted_label_artifact_generator_ready"
        ],
        "offline_predicted_label_artifact_readiness_ready": ready,
        **{key: artifact_summary[key] for key in expected_without_self},
        "numeric_weight_added_count": artifact_summary["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": artifact_summary[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": artifact_summary[
            "role_count_voting_added_count"
        ],
        "historical_tuning_leakage_count": artifact_summary[
            "historical_tuning_leakage_count"
        ],
        "tmp_predicted_label_artifacts_allowed": storage[
            "tmp_predicted_label_artifacts_allowed"
        ],
        "committed_predicted_label_artifacts_allowed": storage[
            "committed_predicted_label_artifacts_allowed"
        ],
        "data_backtests_write_allowed": storage["data_backtests_write_allowed"],
        "data_prospective_write_allowed": storage[
            "data_prospective_write_allowed"
        ],
        "public_output_allowed": storage["public_output_allowed"],
        "artifact_summary": artifact_summary,
        "readiness": readiness,
    }
