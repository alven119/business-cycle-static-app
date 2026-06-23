from __future__ import annotations

from business_cycle.audits.historical_validation_readiness import (
    summarize_historical_validation_readiness,
)


def main() -> None:
    summary = summarize_historical_validation_readiness()
    for key in (
        "phase",
        "historical_validation_readiness_ready",
        "historical_validation_manifest_contract_ready",
        "historical_validation_scenario_manifest_ready",
        "validation_label_policy_ready",
        "scenario_count",
        "point_in_time_requirement_present",
        "label_provenance_complete",
        "label_runtime_usage_prohibited",
        "no_tuning_after_manifest_rule_present",
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
