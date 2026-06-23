from __future__ import annotations

from business_cycle.validation.historical_validation_input_readiness import (
    summarize_historical_validation_input_readiness,
)


def main() -> None:
    summary = summarize_historical_validation_input_readiness()
    for key in (
        "phase",
        "contract_id",
        "contract_version",
        "historical_validation_input_readiness_contract_ready",
        "scenario_input_requirements_ready",
        "input_readiness_registry_ready",
        "point_in_time_input_availability_ready",
        "scenario_count",
        "scenario_id_mismatch_count",
        "scenario_with_complete_input_contract_count",
        "label_provenance_complete",
        "missing_required_field_count",
        "forbidden_output_field_count",
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
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "production_behavior_change_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
