"""Phase 15 validation readiness registry audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.economic_validation_protocol import (
    summarize_economic_validation_protocol,
)


DEFAULT_READINESS_PATH = Path("specs/audits/validation_readiness_registry.yaml")


def load_validation_readiness_registry(
    path: str | Path = DEFAULT_READINESS_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("validation readiness YAML must be a mapping")
    registry = payload.get("validation_readiness_registry")
    if not isinstance(registry, dict):
        raise ValueError("validation_readiness_registry must be a mapping")
    return registry


def summarize_validation_readiness(
    path: str | Path = DEFAULT_READINESS_PATH,
) -> dict[str, Any]:
    registry = load_validation_readiness_registry(path)
    protocol = summarize_economic_validation_protocol()
    rows = registry["readiness_rows"]
    execution = registry["execution_counters"]
    safety = registry["safety_counters"]
    layer_ids = {row["layer_id"] for row in rows}
    protocol_layer_ids = {
        row["layer_id"] for row in protocol["protocol"]["validation_layers"]
    }
    validation_layer_count = len(rows)
    historical_not_started = _row_status(rows, "historical_accuracy_validation")
    economic_not_started = _row_status(rows, "economic_validation")
    prospective_not_started = _row_status(rows, "prospective_validation")
    no_execution = (
        execution["metric_computation_enabled"] is False
        and execution["backtest_execution_enabled"] is False
        and execution["historical_accuracy_validation_started"] is False
        and execution["economic_validation_started"] is False
        and execution["prospective_validation_started"] is False
        and execution["holdout_registered"] is False
        and execution["candidate_selection_enabled"] is False
        and execution["candidate_phase_emitted"] is False
        and execution["current_phase_emitted"] is False
        and execution["prospective_registry_record_count"] == 0
        and execution["real_registry_write_attempt_count"] == 0
    )
    ready = (
        protocol["economic_validation_protocol_ready"] is True
        and layer_ids == protocol_layer_ids
        and validation_layer_count >= 5
        and historical_not_started
        and economic_not_started
        and prospective_not_started
        and no_execution
        and all(value == 0 for value in safety.values())
    )
    return {
        "phase": "15",
        "validation_readiness_registry_ready": ready,
        "validation_layer_count": validation_layer_count,
        "layer_mismatch_count": len(layer_ids.symmetric_difference(protocol_layer_ids)),
        "retrospective_diagnostic_distinguished_from_validation": protocol[
            "retrospective_diagnostic_distinguished_from_validation"
        ],
        "historical_accuracy_validation_not_started": historical_not_started,
        "economic_validation_not_started": economic_not_started,
        "prospective_validation_not_started": prospective_not_started,
        "holdout_registered": execution["holdout_registered"],
        "metric_computation_enabled": execution["metric_computation_enabled"],
        "backtest_execution_enabled": execution["backtest_execution_enabled"],
        "candidate_selection_enabled": execution["candidate_selection_enabled"],
        "candidate_phase_emitted": execution["candidate_phase_emitted"],
        "current_phase_emitted": execution["current_phase_emitted"],
        "prospective_registry_record_count": execution[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": execution[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": safety["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": safety[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": safety["role_count_voting_added_count"],
        "historical_tuning_leakage_count": safety[
            "historical_tuning_leakage_count"
        ],
        "production_behavior_change_count": safety["production_behavior_change_count"],
        "registry": registry,
        "protocol": protocol,
    }


def _row_status(rows: list[dict[str, Any]], layer_id: str) -> bool:
    for row in rows:
        if row["layer_id"] == layer_id:
            return row["execution_status"] == "not_started"
    return False
