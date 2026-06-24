from __future__ import annotations

from business_cycle.audits.validation_blocker_resolution_readiness import (
    summarize_validation_blocker_resolution_readiness,
)


def main() -> None:
    summary = summarize_validation_blocker_resolution_readiness()
    for key in (
        "phase",
        "readiness_id",
        "readiness_version",
        "validation_blocker_resolution_readiness_ready",
        "genuine_blocker_resolution_protocol_ready",
        "genuine_blocker_work_package_registry_ready",
        "reviewed_genuine_blocker_count",
        "work_package_count",
        "blocker_without_work_package_count",
        "work_package_without_source_blocker_count",
        "work_package_without_allowed_action_count",
        "work_package_without_prohibited_action_count",
        "work_package_without_completion_gate_count",
        "false_resolution_count",
        "blocker_resolution_executed",
        "scenario_promoted_to_comparable_count",
        "evidence_rule_modified_count",
        "predicted_mapping_rule_modified_count",
        "formal_decision_contract_modified_count",
        "threshold_modified_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "metric_computation_scope",
        "backtest_execution_enabled",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "forbidden_repo_output_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
