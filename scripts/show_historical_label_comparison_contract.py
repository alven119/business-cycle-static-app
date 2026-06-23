from __future__ import annotations

from business_cycle.validation.historical_label_comparison_contract import (
    summarize_historical_label_comparison_contract,
)


def main() -> None:
    summary = summarize_historical_label_comparison_contract()
    for key in (
        "phase",
        "contract_id",
        "contract_version",
        "historical_label_comparison_contract_ready",
        "label_runtime_usage_prohibited",
        "required_dry_run_result_count",
        "dry_run_result_registry_ready",
        "dry_run_result_count",
        "label_join_policy_ready",
        "denominator_policy_ready",
        "abstention_handling_policy_ready",
        "blocked_result_handling_policy_ready",
        "missing_result_handling_policy_ready",
        "label_comparison_executed",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
