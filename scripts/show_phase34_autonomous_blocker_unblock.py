from __future__ import annotations

from business_cycle.audits.phase34_autonomous_blocker_unblock import (
    summarize_phase34_autonomous_blocker_unblock,
)


def main() -> None:
    summary = summarize_phase34_autonomous_blocker_unblock()
    for key in (
        "phase",
        "autonomous_blocker_unblock_runtime_ready",
        "post_unblock_validation_rerun_ready",
        "attempted_fix_iteration_count",
        "pre_resolution_blocked_scenario_count",
        "post_resolution_blocked_scenario_count",
        "pre_resolution_comparable_scenario_count",
        "post_resolution_comparable_scenario_count",
        "safe_fixable_blocker_count",
        "unresolved_safe_fixable_blocker_count",
        "all_remaining_blockers_are_genuine",
        "blocker_without_attempted_fix_or_genuine_evidence_count",
        "false_resolution_count",
        "scenario_promoted_without_required_evidence_count",
        "evidence_rule_modified_count",
        "predicted_mapping_rule_modified_count",
        "threshold_modified_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "phase34_resolution_progress_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
