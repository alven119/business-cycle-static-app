from __future__ import annotations

from business_cycle.audits.phase21_metric_preregistration_closure import (
    summarize_phase21_metric_preregistration_closure,
)


def main() -> None:
    summary = summarize_phase21_metric_preregistration_closure()
    for key in (
        "phase",
        "phase_id",
        "north_star_alignment_status",
        "semantic_drift_count",
        "historical_label_comparison_contract_ready",
        "historical_metric_preregistration_ready",
        "historical_metric_registry_ready",
        "metric_readiness_ready",
        "preregistered_metric_count",
        "label_runtime_usage_prohibited",
        "label_comparison_executed",
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
        "real_registry_write_attempt_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "alpha17_freeze_hash_valid",
        "alpha16_parent_preserved",
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
        "phase21_closure_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
