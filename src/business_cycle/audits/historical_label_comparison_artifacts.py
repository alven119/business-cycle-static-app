"""Phase 22 historical label-comparison artifact registry audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_label_joiner import (
    summarize_historical_label_comparison_artifact_generation,
)


DEFAULT_LABEL_COMPARISON_ARTIFACT_REGISTRY_PATH = Path(
    "specs/audits/historical_label_comparison_artifact_registry.yaml"
)


def load_historical_label_comparison_artifact_registry(
    path: str | Path = DEFAULT_LABEL_COMPARISON_ARTIFACT_REGISTRY_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical label comparison artifact registry must map")
    registry = payload.get("historical_label_comparison_artifact_registry")
    if not isinstance(registry, dict):
        raise ValueError(
            "historical_label_comparison_artifact_registry must be a mapping"
        )
    return registry


def summarize_historical_label_comparison_artifacts(
    path: str | Path = DEFAULT_LABEL_COMPARISON_ARTIFACT_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = load_historical_label_comparison_artifact_registry(path)
    generation = summarize_historical_label_comparison_artifact_generation()
    expected = registry["expected_counters"]
    storage = registry["artifact_storage_policy"]
    ready = (
        registry["registry_status"]
        == "tmp_or_in_memory_join_artifacts_only_no_metrics"
        and generation["label_comparison_artifact_contract_ready"] is True
        and generation["scenario_count"] == expected["scenario_count"]
        and generation["label_comparison_artifact_count"]
        == expected["label_comparison_artifact_count"]
        and generation["label_provenance_verified_count"]
        == expected["label_provenance_verified_count"]
        and generation["label_used_by_runtime_count"]
        == expected["label_used_by_runtime_count"]
        and generation["label_comparison_executed"]
        is expected["label_comparison_executed"]
        and generation["metric_computation_enabled"]
        is expected["metric_computation_enabled"]
        and generation["historical_accuracy_metric_count"]
        == expected["historical_accuracy_metric_count"]
        and generation["economic_performance_metric_count"]
        == expected["economic_performance_metric_count"]
        and generation["prohibited_artifact_field_count"]
        == expected["prohibited_artifact_field_count"]
        and generation["candidate_phase_emitted"]
        is expected["candidate_phase_emitted"]
        and generation["current_phase_emitted"] is expected["current_phase_emitted"]
        and storage["committed_artifacts_allowed"] is False
        and storage["tmp_artifacts_allowed"] is True
        and storage["data_backtests_write_allowed"] is False
        and storage["data_prospective_write_allowed"] is False
        and storage["public_output_allowed"] is False
    )
    return {
        "phase": "22",
        "registry_id": registry["registry_id"],
        "registry_version": registry["registry_version"],
        "label_comparison_artifact_registry_ready": ready,
        "label_comparison_artifact_contract_ready": generation[
            "label_comparison_artifact_contract_ready"
        ],
        "label_comparison_artifact_generator_ready": generation[
            "label_comparison_artifact_generator_ready"
        ],
        "label_joiner_ready": generation["label_joiner_ready"],
        "scenario_count": generation["scenario_count"],
        "label_comparison_artifact_count": generation[
            "label_comparison_artifact_count"
        ],
        "label_provenance_verified_count": generation[
            "label_provenance_verified_count"
        ],
        "label_used_by_runtime_count": generation["label_used_by_runtime_count"],
        "label_comparison_executed": generation["label_comparison_executed"],
        "metric_computation_enabled": generation["metric_computation_enabled"],
        "historical_accuracy_metric_count": generation[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": generation[
            "economic_performance_metric_count"
        ],
        "prohibited_artifact_field_count": generation[
            "prohibited_artifact_field_count"
        ],
        "backtest_execution_enabled": generation["backtest_execution_enabled"],
        "holdout_registered": generation["holdout_registered"],
        "candidate_selection_enabled": generation["candidate_selection_enabled"],
        "candidate_phase_emitted": generation["candidate_phase_emitted"],
        "current_phase_emitted": generation["current_phase_emitted"],
        "production_behavior_change_count": generation[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": generation[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": generation[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": generation["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": generation[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": generation[
            "role_count_voting_added_count"
        ],
        "historical_tuning_leakage_count": generation[
            "historical_tuning_leakage_count"
        ],
        "committed_artifacts_allowed": storage["committed_artifacts_allowed"],
        "data_backtests_write_allowed": storage["data_backtests_write_allowed"],
        "data_prospective_write_allowed": storage["data_prospective_write_allowed"],
        "public_output_allowed": storage["public_output_allowed"],
        "registry": registry,
        "generation": generation,
    }
