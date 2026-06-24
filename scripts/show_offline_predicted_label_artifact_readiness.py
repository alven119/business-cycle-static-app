from __future__ import annotations

from business_cycle.audits.offline_predicted_label_artifact_readiness import (
    summarize_offline_predicted_label_artifact_readiness,
)


def main() -> None:
    summary = summarize_offline_predicted_label_artifact_readiness()
    for key in (
        "phase",
        "readiness_id",
        "readiness_version",
        "offline_predicted_label_artifact_contract_ready",
        "offline_predicted_label_artifact_generator_ready",
        "offline_predicted_label_artifact_readiness_ready",
        "scenario_count",
        "research_decision_output_count",
        "predicted_label_artifact_count",
        "predicted_label_output_count",
        "predicted_label_provenance_complete_count",
        "mapping_contract_hash_verified",
        "label_used_by_runtime_count",
        "label_comparison_executed",
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
