from __future__ import annotations

from business_cycle.audits.phase20_historical_validation_dry_run_closure import (
    summarize_phase20_historical_validation_dry_run_closure,
)


def main() -> None:
    summary = summarize_phase20_historical_validation_dry_run_closure()
    for key in (
        "phase",
        "phase_id",
        "north_star_alignment_status",
        "semantic_drift_count",
        "historical_validation_dry_run_contract_ready",
        "historical_validation_dry_run_executed",
        "scenario_count",
        "scenario_dry_run_result_count",
        "locked_execution_plan_used",
        "label_blind_execution_verified",
        "label_used_by_runtime_count",
        "model_execution_count",
        "real_historical_validation_executed",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "holdout_registered",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prohibited_result_field_count",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "alpha16_freeze_hash_valid",
        "alpha15_parent_preserved",
        "qa12_freeze_unchanged",
        "formal_decision_model_ready",
        "candidate_capability_ready",
        "economic_validation_status",
        "data_only_model_economically_validated",
        "independent_validation_ready",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "development_next_phase",
        "prospective_track_next_action",
        "phase20_closure_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
