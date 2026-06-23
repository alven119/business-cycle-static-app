"""Phase 22 label joiner for offline comparison input artifacts."""

from __future__ import annotations

from typing import Any

from business_cycle.validation.historical_label_comparison_artifacts import (
    load_historical_label_comparison_artifact_contract,
    validate_historical_label_comparison_artifact,
)
from business_cycle.validation.historical_validation_dry_run import (
    run_historical_validation_dry_run,
)
from business_cycle.validation.historical_validation_manifest import (
    load_historical_validation_scenario_manifest,
)
from business_cycle.validation.validation_label_policy import (
    summarize_validation_label_policy,
)


RUN_ID = "phase22_historical_label_comparison_artifact_generation_v1"


def build_historical_label_comparison_artifacts() -> dict[str, Any]:
    contract = load_historical_label_comparison_artifact_contract()
    dry_run = run_historical_validation_dry_run()
    manifest = load_historical_validation_scenario_manifest()
    label_policy = summarize_validation_label_policy()
    manifest_rows = {
        row["scenario_id"]: row for row in manifest["scenario_rows"]
    }
    artifacts = [
        _build_joined_artifact(
            dry_run_artifact=artifact,
            manifest_row=manifest_rows[artifact["scenario_id"]],
            contract=contract,
            manifest_id=manifest["manifest_id"],
            label_policy_ready=label_policy["validation_label_policy_ready"],
        )
        for artifact in dry_run["result_artifacts"]
    ]
    validations = [
        validate_historical_label_comparison_artifact(
            artifact,
            contract=contract,
        )
        for artifact in artifacts
    ]
    prohibited_artifact_field_count = sum(
        validation["prohibited_artifact_field_count"]
        for validation in validations
    )
    return {
        "phase": "22",
        "run_id": RUN_ID,
        "scenario_count": dry_run["scenario_count"],
        "label_comparison_artifact_count": len(artifacts),
        "label_provenance_verified_count": sum(
            artifact["label_provenance_verified"] is True
            for artifact in artifacts
        ),
        "label_used_by_runtime_count": sum(
            artifact["label_used_by_runtime"] is True for artifact in artifacts
        ),
        "label_comparison_executed": True,
        "metric_computation_enabled": False,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "prohibited_artifact_field_count": prohibited_artifact_field_count,
        "backtest_execution_enabled": False,
        "holdout_registered": False,
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": any(
            artifact["runtime_result_summary"]["candidate_phase_emitted"]
            for artifact in artifacts
        ),
        "current_phase_emitted": any(
            artifact["runtime_result_summary"]["current_phase_emitted"]
            for artifact in artifacts
        ),
        "production_behavior_change_count": contract["output_restrictions"][
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": contract["output_restrictions"][
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": contract["output_restrictions"][
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(
            contract["disabled_runtime_guards"]["numeric_weight_added"]
        ),
        "arbitrary_threshold_added_count": int(
            contract["disabled_runtime_guards"]["arbitrary_threshold_added"]
        ),
        "role_count_voting_added_count": int(
            contract["disabled_runtime_guards"]["role_count_voting_added"]
        ),
        "historical_tuning_leakage_count": int(
            contract["disabled_runtime_guards"]["historical_tuning_used"]
        ),
        "label_comparison_artifacts": artifacts,
        "artifact_validations": validations,
        "contract": contract,
        "dry_run": dry_run,
        "scenario_manifest": manifest,
        "label_policy": label_policy,
    }


def summarize_historical_label_comparison_artifact_generation() -> dict[str, Any]:
    contract = load_historical_label_comparison_artifact_contract()
    run = build_historical_label_comparison_artifacts()
    gates = contract["readiness_gates"]
    ready = (
        contract["contract_status"] == "artifact_generation_allowed_no_metrics"
        and run["scenario_count"] == contract["scenario_count_required"]
        and run["label_comparison_artifact_count"] == run["scenario_count"]
        and run["label_provenance_verified_count"] == run["scenario_count"]
        and run["label_used_by_runtime_count"] == 0
        and run["label_comparison_executed"] is True
        and run["metric_computation_enabled"] is False
        and run["historical_accuracy_metric_count"] == 0
        and run["economic_performance_metric_count"] == 0
        and run["prohibited_artifact_field_count"] == 0
        and run["candidate_phase_emitted"] is False
        and run["current_phase_emitted"] is False
        and all(
            value is True
            for key, value in gates.items()
            if key != "prohibited_artifact_field_count_required"
        )
        and gates["prohibited_artifact_field_count_required"] == 0
        and all(
            validation["artifact_schema_valid"] is True
            for validation in run["artifact_validations"]
        )
        and all(
            value is False
            for value in contract["disabled_runtime_guards"].values()
        )
    )
    return {
        "phase": "22",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "label_comparison_artifact_contract_ready": ready,
        "label_comparison_artifact_generator_ready": ready,
        "label_joiner_ready": ready,
        **{
            key: run[key]
            for key in (
                "scenario_count",
                "label_comparison_artifact_count",
                "label_provenance_verified_count",
                "label_used_by_runtime_count",
                "label_comparison_executed",
                "metric_computation_enabled",
                "historical_accuracy_metric_count",
                "economic_performance_metric_count",
                "prohibited_artifact_field_count",
                "backtest_execution_enabled",
                "holdout_registered",
                "candidate_selection_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "numeric_weight_added_count",
                "arbitrary_threshold_added_count",
                "role_count_voting_added_count",
                "historical_tuning_leakage_count",
            )
        },
        "artifact_run": run,
    }


def _build_joined_artifact(
    *,
    dry_run_artifact: dict[str, Any],
    manifest_row: dict[str, Any],
    contract: dict[str, Any],
    manifest_id: str,
    label_policy_ready: bool,
) -> dict[str, Any]:
    runtime = dry_run_artifact["non_emitting_runtime_output"]
    scenario_id = dry_run_artifact["scenario_id"]
    label_source_id = manifest_row["label_source_id"]
    label_provenance_verified = bool(
        label_policy_ready
        and manifest_row["label_provenance_complete"] is True
        and dry_run_artifact["label_provenance_verified"] is True
    )
    return {
        "artifact_id": f"phase22_label_join:{scenario_id}:{dry_run_artifact['as_of']}",
        "scenario_id": scenario_id,
        "as_of": dry_run_artifact["as_of"],
        "data_mode": dry_run_artifact["data_mode"],
        "dry_run_result_id": (
            f"{dry_run_artifact['run_id']}:{scenario_id}:{dry_run_artifact['as_of']}"
        ),
        "label_source_id": label_source_id,
        "label_provenance_verified": label_provenance_verified,
        "label_join_status": "joined" if label_provenance_verified else "blocked",
        "label_available_for_offline_comparison": contract["join_policy"][
            "label_available_for_offline_comparison"
        ],
        "label_used_by_runtime": False,
        "runtime_result_summary": {
            "runtime_version": runtime["runtime_version"],
            "readiness_label": runtime["readiness_label"],
            "evaluated_phase_or_layer_count": runtime[
                "evaluated_phase_or_layer_count"
            ],
            "candidate_selection_enabled": runtime[
                "candidate_selection_enabled"
            ],
            "candidate_phase_emitted": runtime["candidate_phase_emitted"],
            "current_phase_emitted": runtime["current_phase_emitted"],
            "abstention_reason_count": len(runtime["abstention_reasons"]),
            "blocked_reason_count": len(runtime["blocked_reason_codes"]),
            "raw_observation_only_reason_count": len(
                runtime["raw_observation_only_reasons"]
            ),
        },
        "abstention_status": (
            "abstained" if dry_run_artifact["abstention_reasons"] else "not_abstained"
        ),
        "blocked_reason_codes": dry_run_artifact["blocked_reason_codes"],
        "allowed_uses": [
            "offline_label_comparison_input_review",
            "label_join_provenance_review",
            "metric_prerequisite_artifact_review",
        ],
        "prohibited_uses": [
            "metric_computation",
            "historical_accuracy_claim",
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "runtime_decision_logic",
            "production_dashboard_output",
        ],
        "trust_metadata": {
            "artifact_schema_version": contract["artifact_schema_version"],
            "scenario_id": scenario_id,
            "scenario_manifest_id": manifest_id,
            "label_source_id": label_source_id,
            "label_provenance_verified": label_provenance_verified,
            "label_used_by_runtime": False,
            "metric_computation_enabled": False,
            "source_dry_run_result_id": dry_run_artifact["run_id"],
            "parent_freeze_id": contract["parent_metric_preregistration_freeze_id"],
            "provenance_complete": label_provenance_verified,
        },
        "metric_computation_enabled": False,
    }
