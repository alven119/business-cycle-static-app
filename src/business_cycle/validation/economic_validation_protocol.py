"""Phase 15 economic validation protocol preregistration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_PROTOCOL_PATH = Path("specs/common/economic_validation_protocol_contract.yaml")
REQUIRED_TOP_LEVEL_FIELDS = {
    "protocol_id",
    "protocol_version",
    "validation_layers",
    "allowed_inputs",
    "prohibited_inputs",
    "required_frozen_artifacts",
    "required_data_modes",
    "point_in_time_requirements",
    "revised_data_limitations",
    "retrospective_diagnostic_policy",
    "historical_accuracy_validation_policy",
    "economic_validation_policy",
    "prospective_validation_policy",
    "holdout_registration_policy",
    "leakage_prevention_rules",
    "metric_preregistration_rules",
    "no_tuning_after_results_rule",
    "output_restrictions",
    "readiness_gates",
    "disabled_runtime_guards",
}


def load_economic_validation_protocol(
    path: str | Path = DEFAULT_PROTOCOL_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("economic validation protocol YAML must be a mapping")
    protocol = payload.get("economic_validation_protocol_contract")
    if not isinstance(protocol, dict):
        raise ValueError("economic_validation_protocol_contract must be a mapping")
    return protocol


def summarize_economic_validation_protocol(
    path: str | Path = DEFAULT_PROTOCOL_PATH,
) -> dict[str, Any]:
    protocol = load_economic_validation_protocol(path)
    missing_fields = sorted(REQUIRED_TOP_LEVEL_FIELDS.difference(protocol))
    guards = protocol["disabled_runtime_guards"]
    output = protocol["output_restrictions"]
    retrospective = protocol["retrospective_diagnostic_policy"]
    historical = protocol["historical_accuracy_validation_policy"]
    economic = protocol["economic_validation_policy"]
    prospective = protocol["prospective_validation_policy"]
    holdout = protocol["holdout_registration_policy"]
    layer_statuses = {
        row["layer_id"]: row["status"] for row in protocol["validation_layers"]
    }
    validation_layer_count = len(protocol["validation_layers"])
    disabled_runtime_guards_hold = all(value is False for value in guards.values())
    no_execution = (
        historical["metric_computation_enabled"] is False
        and output["backtest_execution_enabled"] is False
        and output["performance_metric_computed"] is False
        and output["accuracy_metric_computed"] is False
        and output["candidate_selection_enabled"] is False
        and output["candidate_phase_emitted"] is False
        and output["current_phase_emitted"] is False
        and output["public_output_written"] is False
        and prospective["prospective_registry_record_count"] == 0
        and prospective["prospective_registry_write_attempt_count"] == 0
        and holdout["holdout_registered"] is False
    )
    ready = (
        not missing_fields
        and validation_layer_count >= 5
        and retrospective["distinguished_from_validation"] is True
        and layer_statuses["historical_accuracy_validation"] == "not_started"
        and economic["status"] == "not_started"
        and prospective["status"] == "not_started"
        and disabled_runtime_guards_hold
        and no_execution
    )
    return {
        "phase": "15",
        "protocol_id": protocol["protocol_id"],
        "protocol_version": protocol["protocol_version"],
        "economic_validation_protocol_ready": ready,
        "validation_layer_count": validation_layer_count,
        "missing_required_field_count": len(missing_fields),
        "retrospective_diagnostic_distinguished_from_validation": retrospective[
            "distinguished_from_validation"
        ],
        "historical_accuracy_validation_not_started": (
            layer_statuses["historical_accuracy_validation"] == "not_started"
            and historical["status"] == "not_started"
        ),
        "economic_validation_not_started": economic["status"] == "not_started",
        "prospective_validation_not_started": (
            prospective["status"] == "not_started"
        ),
        "holdout_registered": holdout["holdout_registered"],
        "metric_computation_enabled": historical["metric_computation_enabled"],
        "backtest_execution_enabled": output["backtest_execution_enabled"],
        "candidate_selection_enabled": output["candidate_selection_enabled"],
        "candidate_phase_emitted": output["candidate_phase_emitted"],
        "current_phase_emitted": output["current_phase_emitted"],
        "prospective_registry_record_count": prospective[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": prospective[
            "prospective_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(guards["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(guards["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(guards["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(guards["historical_tuning_used"]),
        "disabled_runtime_guards_hold": disabled_runtime_guards_hold,
        "backtest_or_metric_execution_count": _execution_count(
            historical=historical,
            output=output,
        ),
        "validation_execution_started_count": _validation_started_count(
            historical=historical,
            economic=economic,
            prospective=prospective,
        ),
        "protocol": protocol,
    }


def _execution_count(
    *,
    historical: dict[str, Any],
    output: dict[str, Any],
) -> int:
    return sum(
        int(value)
        for value in (
            historical["metric_computation_enabled"],
            output["backtest_execution_enabled"],
            output["performance_metric_computed"],
            output["accuracy_metric_computed"],
        )
    )


def _validation_started_count(
    *,
    historical: dict[str, Any],
    economic: dict[str, Any],
    prospective: dict[str, Any],
) -> int:
    return sum(
        status != "not_started"
        for status in (
            historical["status"],
            economic["status"],
            prospective["status"],
        )
    )
