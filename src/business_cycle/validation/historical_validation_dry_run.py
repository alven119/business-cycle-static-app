"""Phase 20 controlled historical validation dry-run."""

from __future__ import annotations

from typing import Any

from business_cycle.shadow_model.formal_decision_runtime import (
    run_formal_decision_runtime_diagnostics,
)
from business_cycle.validation.historical_validation_execution_plan import (
    summarize_historical_validation_execution_plan,
)
from business_cycle.validation.historical_validation_execution_readiness import (
    summarize_historical_validation_execution_readiness,
)
from business_cycle.validation.historical_validation_input_readiness import (
    build_scenario_input_readiness_outputs,
)
from business_cycle.validation.historical_validation_result_writer import (
    load_historical_validation_dry_run_contract,
    validate_historical_validation_result_artifact,
)
from business_cycle.validation.validation_label_policy import (
    summarize_validation_label_policy,
)


RUN_ID = "phase20_label_blind_historical_validation_dry_run_v1"
RESULT_SCHEMA_VERSION = "phase20_label_blind_result_artifact_v1"


def run_historical_validation_dry_run() -> dict[str, Any]:
    contract = load_historical_validation_dry_run_contract()
    readiness = summarize_historical_validation_execution_readiness()
    plan = summarize_historical_validation_execution_plan()
    label_policy = summarize_validation_label_policy()
    input_rows = {
        row["scenario_id"]: row for row in build_scenario_input_readiness_outputs()
    }
    if readiness["execution_readiness_gate_ready"] is not True:
        raise ValueError("Phase 20 requires Phase 19 execution readiness gate")
    if plan["plan_id"] != contract["locked_execution_plan_id"]:
        raise ValueError("Phase 20 must use the locked Phase 19 execution plan")
    artifacts = [
        _build_result_artifact(
            row=row,
            contract=contract,
            input_row=input_rows[row["scenario_id"]],
            label_policy_ready=label_policy["validation_label_policy_ready"],
        )
        for row in plan["plan"]["scenario_plan_rows"]
    ]
    validations = [
        validate_historical_validation_result_artifact(artifact, contract=contract)
        for artifact in artifacts
    ]
    prohibited_result_field_count = sum(
        validation["prohibited_result_field_count"] for validation in validations
    )
    return {
        "phase": "20",
        "run_id": RUN_ID,
        "historical_validation_dry_run_executed": True,
        "scenario_count": plan["scenario_count"],
        "scenario_dry_run_result_count": len(artifacts),
        "locked_execution_plan_used": plan["plan_id"]
        == contract["locked_execution_plan_id"],
        "label_blind_execution_verified": all(
            artifact["label_used_by_runtime"] is False for artifact in artifacts
        ),
        "label_used_by_runtime_count": sum(
            artifact["label_used_by_runtime"] is True for artifact in artifacts
        ),
        "model_execution_count": sum(
            artifact["decision_runtime_executed"] is True for artifact in artifacts
        ),
        "real_historical_validation_executed": True,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_enabled": False,
        "backtest_execution_enabled": False,
        "holdout_registered": False,
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": any(
            artifact["candidate_phase_emitted"] for artifact in artifacts
        ),
        "current_phase_emitted": any(
            artifact["current_phase_emitted"] for artifact in artifacts
        ),
        "prohibited_result_field_count": prohibited_result_field_count,
        "production_behavior_change_count": contract["production_isolation_policy"][
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": contract["prospective_policy"][
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": contract["prospective_policy"][
            "prospective_registry_write_attempt_count"
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
        "result_artifacts": artifacts,
        "artifact_validations": validations,
        "contract": contract,
        "readiness": readiness,
        "plan": plan,
        "label_policy": label_policy,
    }


def summarize_historical_validation_dry_run() -> dict[str, Any]:
    contract = load_historical_validation_dry_run_contract()
    dry_run = run_historical_validation_dry_run()
    ready = (
        contract["contract_status"]
        == "controlled_label_blind_dry_run_result_artifacts_only"
        and dry_run["historical_validation_dry_run_executed"] is True
        and dry_run["scenario_count"] == contract["dry_run_policy"][
            "scenario_count_required"
        ]
        and dry_run["scenario_dry_run_result_count"] == dry_run["scenario_count"]
        and dry_run["locked_execution_plan_used"] is True
        and dry_run["label_blind_execution_verified"] is True
        and dry_run["label_used_by_runtime_count"] == 0
        and dry_run["model_execution_count"] == dry_run["scenario_count"]
        and dry_run["historical_accuracy_metric_count"] == 0
        and dry_run["economic_performance_metric_count"] == 0
        and dry_run["metric_computation_enabled"] is False
        and dry_run["backtest_execution_enabled"] is False
        and dry_run["candidate_phase_emitted"] is False
        and dry_run["current_phase_emitted"] is False
        and dry_run["prohibited_result_field_count"] == 0
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "phase": "20",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "historical_validation_dry_run_contract_ready": ready,
        **{
            key: dry_run[key]
            for key in (
                "historical_validation_dry_run_executed",
                "scenario_count",
                "scenario_dry_run_result_count",
                "locked_execution_plan_used",
                "label_blind_execution_verified",
                "label_used_by_runtime_count",
                "model_execution_count",
                "real_historical_validation_executed",
                "historical_accuracy_metric_count",
                "economic_performance_metric_count",
                "metric_computation_enabled",
                "backtest_execution_enabled",
                "holdout_registered",
                "candidate_selection_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "prohibited_result_field_count",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "numeric_weight_added_count",
                "arbitrary_threshold_added_count",
                "role_count_voting_added_count",
                "historical_tuning_leakage_count",
            )
        },
        "dry_run": dry_run,
    }


def _build_result_artifact(
    *,
    row: dict[str, Any],
    contract: dict[str, Any],
    input_row: dict[str, Any],
    label_policy_ready: bool,
) -> dict[str, Any]:
    runtime_output = run_formal_decision_runtime_diagnostics(
        as_of=row["as_of"],
        data_mode=row["data_mode"],
    )
    return {
        "run_id": RUN_ID,
        "scenario_id": row["scenario_id"],
        "as_of": row["as_of"],
        "data_mode": row["data_mode"],
        "freeze_id": contract["parent_freeze_id"],
        "execution_plan_id": contract["locked_execution_plan_id"],
        "input_artifact_ids": row["required_input_artifacts"],
        "label_provenance_verified": bool(
            label_policy_ready
            and row["required_label_artifacts"]
            and input_row["label_provenance_status"] == "complete"
        ),
        "label_used_by_runtime": False,
        "decision_runtime_executed": True,
        "non_emitting_runtime_output": runtime_output,
        "abstention_reasons": runtime_output["abstention_reasons"],
        "blocked_reason_codes": sorted(
            set(runtime_output["blocked_reason_codes"])
            | {
                "candidate_output_disabled",
                "metric_computation_disabled",
                "backtest_execution_disabled",
                "label_blind_runtime",
            }
        ),
        "trust_metadata": {
            "artifact_schema_version": RESULT_SCHEMA_VERSION,
            "scenario_id": row["scenario_id"],
            "as_of": row["as_of"],
            "data_mode": row["data_mode"],
            "execution_plan_id": contract["locked_execution_plan_id"],
            "parent_freeze_id": contract["parent_freeze_id"],
            "runtime_freeze_id": contract["runtime_freeze_id"],
            "label_provenance_verified": True,
            "label_used_by_runtime": False,
            "provenance_complete": True,
        },
        "allowed_uses": [
            "label_blind_validation_dry_run_artifact_review",
            "validation_execution_plumbing_check",
            "provenance_and_abstention_diagnostics",
        ],
        "prohibited_uses": [
            "historical_accuracy_claim",
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "backtest_or_portfolio_research",
            "production_dashboard_output",
        ],
        "metric_computation_enabled": False,
        "backtest_execution_enabled": False,
        "candidate_phase_emitted": runtime_output["candidate_phase_emitted"],
        "current_phase_emitted": runtime_output["current_phase_emitted"],
    }
