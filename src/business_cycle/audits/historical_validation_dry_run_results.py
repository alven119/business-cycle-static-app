"""Phase 20 dry-run result artifact registry audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_validation_dry_run import (
    summarize_historical_validation_dry_run,
)


DEFAULT_REGISTRY_PATH = Path(
    "specs/audits/historical_validation_dry_run_result_registry.yaml"
)


def load_historical_validation_dry_run_result_registry(
    path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation dry-run result registry must map")
    registry = payload.get("historical_validation_dry_run_result_registry")
    if not isinstance(registry, dict):
        raise ValueError(
            "historical_validation_dry_run_result_registry must be a mapping"
        )
    return registry


def summarize_historical_validation_dry_run_results(
    path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = load_historical_validation_dry_run_result_registry(path)
    dry_run = summarize_historical_validation_dry_run()
    expected = registry["expected_counters"]
    storage = registry["artifact_storage_policy"]
    ready = (
        registry["registry_status"] == "in_memory_or_tmp_result_artifacts_only"
        and dry_run["historical_validation_dry_run_contract_ready"] is True
        and dry_run["scenario_count"] == expected["scenario_count"]
        and dry_run["scenario_dry_run_result_count"]
        == expected["scenario_dry_run_result_count"]
        and dry_run["model_execution_count"] == expected["model_execution_count"]
        and dry_run["real_historical_validation_executed"]
        is expected["real_historical_validation_executed"]
        and dry_run["label_used_by_runtime_count"]
        == expected["label_used_by_runtime_count"]
        and dry_run["historical_accuracy_metric_count"]
        == expected["historical_accuracy_metric_count"]
        and dry_run["economic_performance_metric_count"]
        == expected["economic_performance_metric_count"]
        and dry_run["prohibited_result_field_count"]
        == expected["prohibited_result_field_count"]
        and dry_run["candidate_phase_emitted"]
        is expected["candidate_phase_emitted"]
        and dry_run["current_phase_emitted"] is expected["current_phase_emitted"]
        and storage["committed_artifacts_allowed"] is False
        and storage["tmp_artifacts_allowed"] is True
        and storage["data_backtests_write_allowed"] is False
        and storage["data_prospective_write_allowed"] is False
        and storage["public_output_allowed"] is False
    )
    return {
        "phase": "20",
        "registry_id": registry["registry_id"],
        "registry_version": registry["registry_version"],
        "historical_validation_dry_run_result_registry_ready": ready,
        "scenario_count": dry_run["scenario_count"],
        "scenario_dry_run_result_count": dry_run[
            "scenario_dry_run_result_count"
        ],
        "model_execution_count": dry_run["model_execution_count"],
        "real_historical_validation_executed": dry_run[
            "real_historical_validation_executed"
        ],
        "label_blind_execution_verified": dry_run[
            "label_blind_execution_verified"
        ],
        "label_used_by_runtime_count": dry_run["label_used_by_runtime_count"],
        "historical_accuracy_metric_count": dry_run[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": dry_run[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": dry_run["metric_computation_enabled"],
        "backtest_execution_enabled": dry_run["backtest_execution_enabled"],
        "prohibited_result_field_count": dry_run["prohibited_result_field_count"],
        "candidate_phase_emitted": dry_run["candidate_phase_emitted"],
        "current_phase_emitted": dry_run["current_phase_emitted"],
        "committed_artifacts_allowed": storage["committed_artifacts_allowed"],
        "data_backtests_write_allowed": storage["data_backtests_write_allowed"],
        "data_prospective_write_allowed": storage["data_prospective_write_allowed"],
        "public_output_allowed": storage["public_output_allowed"],
        "registry": registry,
        "dry_run": dry_run,
    }
