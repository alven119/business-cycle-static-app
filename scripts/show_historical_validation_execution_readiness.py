from __future__ import annotations

from business_cycle.validation.historical_validation_execution_readiness import (
    summarize_historical_validation_execution_readiness,
)


def main() -> None:
    summary = summarize_historical_validation_execution_readiness()
    for key in (
        "phase",
        "contract_id",
        "contract_version",
        "historical_validation_execution_readiness_contract_ready",
        "historical_validation_execution_plan_ready",
        "result_artifact_contract_ready",
        "scenario_count",
        "scenario_with_execution_plan_count",
        "prior_freeze_dependency_complete",
        "decision_runtime_dependency_complete",
        "validation_protocol_dependency_complete",
        "validation_harness_dependency_complete",
        "input_readiness_dependency_complete",
        "label_policy_dependency_complete",
        "execution_allowed_in_this_phase",
        "missing_required_field_count",
        "model_execution_count",
        "real_historical_validation_executed",
        "historical_validation_result_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
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
        "execution_readiness_gate_ready",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
