from __future__ import annotations

from business_cycle.audits.historical_validation_dry_run_results import (
    summarize_historical_validation_dry_run_results,
)


def main() -> None:
    summary = summarize_historical_validation_dry_run_results()
    for key in (
        "phase",
        "registry_id",
        "registry_version",
        "historical_validation_dry_run_result_registry_ready",
        "scenario_count",
        "scenario_dry_run_result_count",
        "model_execution_count",
        "real_historical_validation_executed",
        "label_blind_execution_verified",
        "label_used_by_runtime_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "prohibited_result_field_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "committed_artifacts_allowed",
        "data_backtests_write_allowed",
        "data_prospective_write_allowed",
        "public_output_allowed",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
