from __future__ import annotations

from business_cycle.audits.shadow_autonomous_blocker_unblock_freeze import (
    summarize_shadow_autonomous_blocker_unblock_freeze,
)


def main() -> None:
    summary = summarize_shadow_autonomous_blocker_unblock_freeze()
    for key in (
        "phase",
        "autonomous_blocker_unblock_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_type",
        "freeze_manifest_hash",
        "alpha30_freeze_hash_valid",
        "alpha29_parent_preserved",
        "qa12_freeze_unchanged",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "autonomous_blocker_unblock_runtime_ready",
        "post_unblock_validation_rerun_ready",
        "attempted_fix_iteration_count",
        "pre_resolution_blocked_scenario_count",
        "post_resolution_blocked_scenario_count",
        "false_resolution_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "prospective_registry_write_attempt_count",
        "economic_validation_status",
        "book_alignment_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
