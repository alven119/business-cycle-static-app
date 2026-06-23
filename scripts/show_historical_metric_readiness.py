from __future__ import annotations

from business_cycle.audits.historical_metric_readiness import (
    summarize_historical_metric_readiness,
)


def main() -> None:
    summary = summarize_historical_metric_readiness()
    for key in (
        "phase",
        "historical_label_comparison_contract_ready",
        "historical_metric_preregistration_ready",
        "historical_metric_registry_ready",
        "metric_readiness_ready",
        "preregistered_metric_count",
        "label_runtime_usage_prohibited",
        "label_comparison_executed",
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
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
