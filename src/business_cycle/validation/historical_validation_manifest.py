"""Phase 17 historical validation manifest preregistration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONTRACT_PATH = Path("specs/common/historical_validation_manifest_contract.yaml")
DEFAULT_SCENARIO_MANIFEST_PATH = Path(
    "specs/audits/historical_validation_scenario_manifest.yaml"
)
REQUIRED_CONTRACT_FIELDS = {
    "manifest_id",
    "manifest_version",
    "scenario_selection_policy",
    "scenario_ids",
    "validation_window_definitions",
    "allowed_data_modes",
    "point_in_time_requirements",
    "revised_data_allowed_only_for_declared_comparison",
    "label_source_policy",
    "label_provenance_requirements",
    "label_usage_restrictions",
    "exclusion_policy",
    "leakage_prevention_rules",
    "no_tuning_after_manifest_rule",
    "metric_preregistration_dependency",
    "output_restrictions",
    "readiness_gates",
    "disabled_runtime_guards",
}


def load_historical_validation_manifest_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation manifest contract must be a mapping")
    contract = payload.get("historical_validation_manifest_contract")
    if not isinstance(contract, dict):
        raise ValueError("historical_validation_manifest_contract must be a mapping")
    return contract


def load_historical_validation_scenario_manifest(
    path: str | Path = DEFAULT_SCENARIO_MANIFEST_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation scenario manifest must be a mapping")
    manifest = payload.get("historical_validation_scenario_manifest")
    if not isinstance(manifest, dict):
        raise ValueError("historical_validation_scenario_manifest must be a mapping")
    return manifest


def summarize_historical_validation_manifest(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    scenario_manifest_path: str | Path = DEFAULT_SCENARIO_MANIFEST_PATH,
) -> dict[str, Any]:
    contract = load_historical_validation_manifest_contract(contract_path)
    manifest = load_historical_validation_scenario_manifest(scenario_manifest_path)
    rows = manifest["scenario_rows"]
    scenario_ids = set(contract["scenario_ids"])
    row_ids = {row["scenario_id"] for row in rows}
    window_ids = {
        row["scenario_id"] for row in contract["validation_window_definitions"]
    }
    missing_fields = sorted(REQUIRED_CONTRACT_FIELDS.difference(contract))
    output = contract["output_restrictions"]
    guards = contract["disabled_runtime_guards"]
    counters = manifest["manifest_counters"]
    point_in_time_requirement_present = (
        contract["point_in_time_requirements"]["point_in_time_required"] is True
        and all(row["point_in_time_required"] is True for row in rows)
    )
    label_provenance_complete = all(
        row["label_provenance_complete"] is True for row in rows
    )
    no_tuning_after_manifest_rule_present = (
        contract["no_tuning_after_manifest_rule"]["enabled"] is True
        and contract["no_tuning_after_manifest_rule"][
            "rule_or_threshold_change_requires_new_freeze"
        ]
        is True
    )
    no_execution = (
        output["real_historical_validation_executed"] is False
        and output["historical_accuracy_metric_count"] == 0
        and output["economic_performance_metric_count"] == 0
        and output["metric_computation_enabled"] is False
        and output["backtest_execution_enabled"] is False
        and output["holdout_registered"] is False
        and output["candidate_selection_enabled"] is False
        and output["candidate_phase_emitted"] is False
        and output["current_phase_emitted"] is False
        and counters["real_historical_validation_executed"] is False
        and counters["historical_accuracy_metric_count"] == 0
        and counters["economic_performance_metric_count"] == 0
        and counters["metric_computation_enabled"] is False
        and counters["backtest_execution_enabled"] is False
        and counters["candidate_selection_enabled"] is False
        and counters["candidate_phase_emitted"] is False
        and counters["current_phase_emitted"] is False
        and counters["prospective_registry_record_count"] == 0
        and counters["real_registry_write_attempt_count"] == 0
    )
    scenario_execution_started_count = sum(
        row["validation_execution_status"] != "not_started" for row in rows
    )
    metric_or_backtest_count = sum(
        int(row["metric_computed"]) + int(row["backtest_executed"]) for row in rows
    )
    candidate_or_current_phase_read_count = sum(
        int(row["candidate_or_current_phase_read"]) for row in rows
    )
    ready = (
        not missing_fields
        and scenario_ids == row_ids == window_ids
        and len(rows) > 0
        and contract["scenario_selection_policy"][
            "selection_made_before_validation_execution"
        ]
        is True
        and contract["scenario_selection_policy"]["result_based_selection_allowed"]
        is False
        and point_in_time_requirement_present
        and contract["revised_data_allowed_only_for_declared_comparison"] is True
        and label_provenance_complete
        and no_tuning_after_manifest_rule_present
        and no_execution
        and scenario_execution_started_count == 0
        and metric_or_backtest_count == 0
        and candidate_or_current_phase_read_count == 0
        and all(value is False for value in guards.values())
    )
    return {
        "phase": "17",
        "manifest_id": contract["manifest_id"],
        "manifest_version": contract["manifest_version"],
        "historical_validation_manifest_contract_ready": (
            not missing_fields and contract["readiness_gates"][
                "historical_validation_manifest_contract_ready"
            ]
            is True
        ),
        "historical_validation_scenario_manifest_ready": ready,
        "scenario_count": len(rows),
        "scenario_id_mismatch_count": len(scenario_ids.symmetric_difference(row_ids)),
        "window_definition_mismatch_count": len(
            scenario_ids.symmetric_difference(window_ids)
        ),
        "missing_required_field_count": len(missing_fields),
        "point_in_time_requirement_present": point_in_time_requirement_present,
        "revised_data_allowed_only_for_declared_comparison": contract[
            "revised_data_allowed_only_for_declared_comparison"
        ],
        "label_provenance_complete": label_provenance_complete,
        "scenario_without_label_provenance_count": sum(
            row["label_provenance_complete"] is not True for row in rows
        ),
        "label_runtime_usage_prohibited": contract["label_usage_restrictions"][
            "runtime_decision_logic_allowed"
        ]
        is False,
        "no_tuning_after_manifest_rule_present": (
            no_tuning_after_manifest_rule_present
        ),
        "real_historical_validation_executed": output[
            "real_historical_validation_executed"
        ],
        "historical_accuracy_metric_count": output[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": output[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": output["metric_computation_enabled"],
        "backtest_execution_enabled": output["backtest_execution_enabled"],
        "holdout_registered": output["holdout_registered"],
        "candidate_selection_enabled": output["candidate_selection_enabled"],
        "candidate_phase_emitted": output["candidate_phase_emitted"],
        "current_phase_emitted": output["current_phase_emitted"],
        "prospective_registry_record_count": counters[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": counters[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(guards["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(guards["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(guards["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(guards["historical_tuning_used"]),
        "scenario_execution_started_count": scenario_execution_started_count,
        "metric_or_backtest_count": metric_or_backtest_count,
        "candidate_or_current_phase_read_count": candidate_or_current_phase_read_count,
        "disabled_runtime_guards_hold": all(
            value is False for value in guards.values()
        ),
        "contract": contract,
        "scenario_manifest": manifest,
    }
