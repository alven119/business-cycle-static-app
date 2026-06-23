from __future__ import annotations

from business_cycle.validation.historical_metric_preregistration import (
    summarize_historical_metric_preregistration,
    summarize_historical_metric_registry,
)


def main() -> None:
    registry = summarize_historical_metric_registry()
    preregistration = summarize_historical_metric_preregistration()
    summary = registry | {
        "historical_metric_preregistration_ready": preregistration[
            "historical_metric_preregistration_ready"
        ],
        "label_runtime_usage_prohibited": preregistration[
            "label_runtime_usage_prohibited"
        ],
        "metric_computation_enabled": preregistration[
            "metric_computation_enabled"
        ],
        "backtest_execution_enabled": preregistration[
            "backtest_execution_enabled"
        ],
        "candidate_phase_emitted": preregistration["candidate_phase_emitted"],
        "current_phase_emitted": preregistration["current_phase_emitted"],
    }
    for key in (
        "phase",
        "registry_id",
        "registry_version",
        "historical_metric_preregistration_ready",
        "historical_metric_registry_ready",
        "preregistered_metric_count",
        "computation_enabled_metric_count",
        "metric_without_denominator_count",
        "metric_without_abstention_policy_count",
        "metric_without_blocked_policy_count",
        "metric_without_missing_policy_count",
        "label_runtime_usage_prohibited",
        "label_comparison_executed",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
