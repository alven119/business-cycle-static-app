from __future__ import annotations

from business_cycle.audits.shadow_historical_dry_run_freeze import (
    summarize_shadow_historical_dry_run_freeze,
)


def main() -> None:
    summary = summarize_shadow_historical_dry_run_freeze()
    for key in (
        "phase",
        "historical_dry_run_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_type",
        "freeze_manifest_hash",
        "alpha16_freeze_hash_valid",
        "alpha15_parent_preserved",
        "parent_freeze_present",
        "qa12_freeze_unchanged",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "historical_validation_dry_run_executed",
        "result_artifacts_only",
        "locked_execution_plan_used",
        "label_blind_execution_verified",
        "label_used_by_runtime_count",
        "model_execution_count",
        "real_historical_validation_executed",
        "historical_validation_result_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "holdout_registered",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "prospective_registry_write_attempt_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "formal_decision_model_ready",
        "candidate_capability_ready",
        "economic_validation_status",
        "book_alignment_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
