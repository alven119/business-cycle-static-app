from __future__ import annotations

from business_cycle.audits.phase25_research_decision_output_closure import (
    summarize_phase25_research_decision_output_closure,
)


def main() -> None:
    summary = summarize_phase25_research_decision_output_closure()
    for key in (
        "phase",
        "phase_id",
        "north_star_alignment_status",
        "semantic_drift_count",
        "research_decision_output_artifact_contract_ready",
        "research_decision_output_runtime_ready",
        "research_decision_output_registry_ready",
        "scenario_count",
        "research_decision_output_count",
        "output_mode_research_only_count",
        "predicted_label_output_count",
        "label_used_by_runtime_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_scope",
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
        "alpha21_freeze_hash_valid",
        "alpha20_parent_preserved",
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
        "phase25_closure_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
