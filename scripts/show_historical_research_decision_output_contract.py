from __future__ import annotations

from business_cycle.validation.historical_research_decision_output_contract import (
    summarize_historical_research_decision_output_contract,
)


def main() -> None:
    summary = summarize_historical_research_decision_output_contract()
    for key in (
        "phase",
        "contract_id",
        "contract_version",
        "research_decision_output_contract_ready",
        "output_taxonomy_ready",
        "future_allowed_field_count",
        "forbidden_output_field_count",
        "predicted_label_output_count",
        "research_decision_output_emitted",
        "label_used_by_runtime_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "accuracy_metric_enabled",
        "economic_performance_metric_enabled",
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
