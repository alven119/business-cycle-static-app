from __future__ import annotations

from business_cycle.audits.phase33_genuine_blocker_resolution_execution import (
    summarize_phase33_genuine_blocker_resolution_execution,
)


def main() -> None:
    summary = summarize_phase33_genuine_blocker_resolution_execution()
    for key in (
        "phase",
        "genuine_blocker_resolution_execution_ready",
        "post_resolution_validation_rerun_ready",
        "work_package_count",
        "safe_executable_work_package_count",
        "executed_work_package_count",
        "still_genuine_blocked_work_package_count",
        "work_package_without_execution_reason_count",
        "pre_resolution_blocked_scenario_count",
        "post_resolution_blocked_scenario_count",
        "pre_resolution_comparable_scenario_count",
        "post_resolution_comparable_scenario_count",
        "false_resolution_count",
        "scenario_promoted_without_required_evidence_count",
        "scenario_promoted_by_taxonomy_only_count",
        "scenario_promoted_by_modern_proxy_count",
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
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "forbidden_repo_output_count",
        "phase33_resolution_progress_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
