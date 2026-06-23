"""Phase 18 historical validation input readiness audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.historical_validation_scenario_inputs import (
    summarize_historical_validation_scenario_inputs,
)
from business_cycle.validation.historical_validation_manifest import (
    summarize_historical_validation_manifest,
)
from business_cycle.validation.point_in_time_input_availability import (
    summarize_point_in_time_input_availability,
)
from business_cycle.validation.validation_label_policy import (
    summarize_validation_label_policy,
)


DEFAULT_CONTRACT_PATH = Path(
    "specs/common/historical_validation_input_readiness_contract.yaml"
)
DEFAULT_REGISTRY_PATH = Path(
    "specs/audits/historical_validation_input_readiness_registry.yaml"
)
REQUIRED_CONTRACT_FIELDS = {
    "contract_id",
    "contract_version",
    "scenario_manifest_dependency",
    "label_policy_dependency",
    "required_frozen_artifacts",
    "scenario_input_requirements",
    "required_series_policy",
    "required_vintage_policy",
    "required_release_metadata_policy",
    "point_in_time_availability_policy",
    "revised_data_comparison_policy",
    "missing_input_policy",
    "unavailable_input_policy",
    "abstention_expected_when_missing_policy",
    "no_network_policy_for_tests",
    "no_model_execution_policy",
    "no_metric_computation_policy",
    "output_restrictions",
    "readiness_gates",
    "disabled_runtime_guards",
}


def load_historical_validation_input_readiness_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation input readiness contract must map")
    contract = payload.get("historical_validation_input_readiness_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_validation_input_readiness_contract must be a mapping"
        )
    return contract


def load_historical_validation_input_readiness_registry(
    path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation input readiness registry must map")
    registry = payload.get("historical_validation_input_readiness_registry")
    if not isinstance(registry, dict):
        raise ValueError(
            "historical_validation_input_readiness_registry must be a mapping"
        )
    return registry


def summarize_historical_validation_input_readiness(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    contract = load_historical_validation_input_readiness_contract(contract_path)
    registry = load_historical_validation_input_readiness_registry(registry_path)
    manifest = summarize_historical_validation_manifest()
    label_policy = summarize_validation_label_policy()
    scenario_inputs = summarize_historical_validation_scenario_inputs()
    rows = registry["readiness_rows"]
    output = contract["output_restrictions"]
    guards = contract["disabled_runtime_guards"]
    execution = registry["execution_counters"]
    safety = registry["safety_counters"]
    missing_fields = sorted(REQUIRED_CONTRACT_FIELDS.difference(contract))
    scenario_ids = {row["scenario_id"] for row in rows}
    manifest_ids = {
        row["scenario_id"]
        for row in manifest["scenario_manifest"]["scenario_rows"]
    }
    forbidden_output_field_count = _forbidden_output_field_count(
        rows,
        contract["forbidden_outputs"],
    )
    point_in_time = summarize_point_in_time_input_availability(rows=rows)
    no_execution = (
        output["model_execution_count"] == 0
        and output["real_historical_validation_executed"] is False
        and output["historical_accuracy_metric_count"] == 0
        and output["economic_performance_metric_count"] == 0
        and output["metric_computation_enabled"] is False
        and output["backtest_execution_enabled"] is False
        and output["holdout_registered"] is False
        and output["candidate_selection_enabled"] is False
        and output["candidate_phase_emitted"] is False
        and output["current_phase_emitted"] is False
        and execution["model_execution_count"] == 0
        and execution["real_historical_validation_executed"] is False
        and execution["historical_accuracy_metric_count"] == 0
        and execution["economic_performance_metric_count"] == 0
        and execution["metric_computation_enabled"] is False
        and execution["backtest_execution_enabled"] is False
        and execution["holdout_registered"] is False
        and execution["candidate_selection_enabled"] is False
        and execution["candidate_phase_emitted"] is False
        and execution["current_phase_emitted"] is False
        and execution["prospective_registry_record_count"] == 0
        and execution["real_registry_write_attempt_count"] == 0
    )
    ready = (
        not missing_fields
        and registry["registry_status"] == "input_readiness_audited_no_model_execution"
        and manifest["historical_validation_scenario_manifest_ready"] is True
        and label_policy["validation_label_policy_ready"] is True
        and scenario_inputs["scenario_input_requirements_ready"] is True
        and scenario_ids == manifest_ids
        and len(rows) == manifest["scenario_count"]
        and point_in_time["point_in_time_input_availability_ready"] is True
        and forbidden_output_field_count == 0
        and no_execution
        and all(value is False for value in guards.values())
        and all(value == 0 for value in safety.values())
    )
    return {
        "phase": "18",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "historical_validation_input_readiness_contract_ready": (
            not missing_fields
            and contract["readiness_gates"][
                "historical_validation_input_readiness_contract_ready"
            ]
            is True
        ),
        "scenario_input_requirements_ready": scenario_inputs[
            "scenario_input_requirements_ready"
        ],
        "input_readiness_registry_ready": ready,
        "point_in_time_input_availability_ready": point_in_time[
            "point_in_time_input_availability_ready"
        ],
        "scenario_count": len(rows),
        "scenario_id_mismatch_count": len(scenario_ids.symmetric_difference(manifest_ids)),
        "scenario_with_complete_input_contract_count": scenario_inputs[
            "scenario_with_complete_input_contract_count"
        ],
        "label_provenance_complete": (
            scenario_inputs["label_provenance_complete"]
            and label_policy["label_provenance_complete"]
        ),
        "missing_required_field_count": len(missing_fields),
        "forbidden_output_field_count": forbidden_output_field_count,
        "model_execution_count": execution["model_execution_count"],
        "real_historical_validation_executed": execution[
            "real_historical_validation_executed"
        ],
        "historical_accuracy_metric_count": execution[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": execution[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": execution["metric_computation_enabled"],
        "backtest_execution_enabled": execution["backtest_execution_enabled"],
        "holdout_registered": execution["holdout_registered"],
        "candidate_selection_enabled": execution["candidate_selection_enabled"],
        "candidate_phase_emitted": execution["candidate_phase_emitted"],
        "current_phase_emitted": execution["current_phase_emitted"],
        "prospective_registry_record_count": execution[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": execution[
            "real_registry_write_attempt_count"
        ],
        "production_behavior_change_count": safety["production_behavior_change_count"],
        "numeric_weight_added_count": safety["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": safety[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": safety["role_count_voting_added_count"],
        "historical_tuning_leakage_count": safety[
            "historical_tuning_leakage_count"
        ],
        "point_in_time": point_in_time,
        "scenario_inputs": scenario_inputs,
        "registry": registry,
        "contract": contract,
        "manifest": manifest,
        "label_policy": label_policy,
    }


def build_scenario_input_readiness_outputs() -> list[dict[str, Any]]:
    registry = load_historical_validation_input_readiness_registry()
    return [
        {
            "scenario_id": row["scenario_id"],
            "required_input_count": row["required_input_count"],
            "available_input_count": row["available_input_count"],
            "missing_input_count": row["missing_input_count"],
            "unavailable_input_count": row["unavailable_input_count"],
            "required_vintage_count": row["required_vintage_count"],
            "available_vintage_count": row["available_vintage_count"],
            "missing_vintage_count": row["missing_vintage_count"],
            "label_provenance_status": row["label_provenance_status"],
            "point_in_time_readiness_status": row[
                "point_in_time_readiness_status"
            ],
            "blocked_reason_codes": row["blocked_reason_codes"],
            "readiness_label": row["readiness_label"],
            "allowed_uses": registry["allowed_uses"],
            "prohibited_uses": registry["prohibited_uses"],
            "trust_metadata": registry["trust_metadata"],
        }
        for row in registry["readiness_rows"]
    ]


def _forbidden_output_field_count(
    payload: Any,
    forbidden_outputs: list[str],
) -> int:
    forbidden = set(forbidden_outputs)
    return len(forbidden.intersection(_all_keys(payload)))


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(_all_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_all_keys(item))
        return keys
    return set()
