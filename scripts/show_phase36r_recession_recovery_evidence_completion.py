from __future__ import annotations

from business_cycle.audits.phase36r_recession_recovery_evidence_completion import (
    summarize_phase36r_recession_recovery_evidence_completion,
)


def main() -> None:
    summary = summarize_phase36r_recession_recovery_evidence_completion()
    for key in (
        "phase",
        "phase_id",
        "recession_recovery_evidence_completion_runtime_ready",
        "post_evidence_completion_validation_rerun_ready",
        "attempted_fix_iteration_count",
        "scenario_count",
        "target_recession_recovery_scenario_count",
        "pre_comparable_scenario_count",
        "post_comparable_scenario_count",
        "phase_evidence_completion_attempted_scenario_count",
        "safe_fixable_recession_recovery_gap_count",
        "unresolved_safe_fixable_recession_recovery_gap_count",
        "evidence_completion_false_positive_count",
        "false_comparability_count",
        "scenario_promoted_without_required_evidence_count",
        "scenario_promoted_by_taxonomy_only_count",
        "scenario_promoted_by_modern_proxy_count",
        "evidence_rule_semantics_modified_count",
        "predicted_mapping_rule_modified_count",
        "formal_decision_contract_modified_count",
        "threshold_modified_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "metric_computation_scope",
        "economic_performance_metric_count",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "phase36r_progress_status",
        "development_next_phase",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
