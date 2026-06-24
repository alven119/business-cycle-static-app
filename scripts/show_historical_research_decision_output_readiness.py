from __future__ import annotations

from business_cycle.audits.historical_research_decision_output_readiness import (
    summarize_historical_research_decision_output_readiness,
)


def main() -> None:
    summary = summarize_historical_research_decision_output_readiness()
    for key in (
        "phase",
        "readiness_id",
        "readiness_version",
        "research_decision_output_contract_ready",
        "research_decision_output_readiness_ready",
        "output_taxonomy_ready",
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
        "committed_decision_outputs_allowed",
        "data_backtests_write_allowed",
        "data_prospective_write_allowed",
        "public_output_allowed",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
