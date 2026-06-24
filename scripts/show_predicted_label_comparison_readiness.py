from __future__ import annotations

from business_cycle.audits.predicted_label_comparison_readiness import (
    summarize_predicted_label_comparison_readiness,
)


def main() -> None:
    summary = summarize_predicted_label_comparison_readiness()
    for key in (
        "phase",
        "readiness_id",
        "readiness_version",
        "predicted_label_comparison_artifact_contract_ready",
        "predicted_label_comparison_generator_ready",
        "predicted_label_comparison_readiness_ready",
        "scenario_count",
        "predicted_label_artifact_count",
        "label_comparison_artifact_count",
        "label_comparison_executed",
        "predicted_label_provenance_verified_count",
        "historical_label_provenance_verified_count",
        "mapping_contract_hash_verified",
        "label_used_by_runtime_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prohibited_artifact_field_count",
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
