from __future__ import annotations

from business_cycle.audits.offline_predicted_label_mapping_readiness import (
    summarize_offline_predicted_label_mapping_readiness,
)


def main() -> None:
    summary = summarize_offline_predicted_label_mapping_readiness()
    for key in (
        "phase",
        "readiness_id",
        "readiness_version",
        "predicted_label_mapping_contract_ready",
        "predicted_label_mapping_readiness_ready",
        "research_decision_state_taxonomy_ready",
        "offline_predicted_label_taxonomy_ready",
        "mapping_rule_count",
        "predicted_label_output_count",
        "predicted_label_artifact_count",
        "label_comparison_executed",
        "label_used_by_runtime_count",
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
        "committed_predicted_label_artifacts_allowed",
        "tmp_predicted_label_artifacts_allowed",
        "data_backtests_write_allowed",
        "data_prospective_write_allowed",
        "public_output_allowed",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
