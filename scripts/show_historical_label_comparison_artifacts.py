from __future__ import annotations

from business_cycle.audits.historical_label_comparison_artifacts import (
    summarize_historical_label_comparison_artifacts,
)


def main() -> None:
    summary = summarize_historical_label_comparison_artifacts()
    for key in (
        "phase",
        "registry_id",
        "registry_version",
        "label_comparison_artifact_registry_ready",
        "label_comparison_artifact_contract_ready",
        "label_comparison_artifact_generator_ready",
        "label_joiner_ready",
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
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
