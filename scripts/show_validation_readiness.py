from __future__ import annotations

from business_cycle.audits.validation_readiness import summarize_validation_readiness


def main() -> None:
    summary = summarize_validation_readiness()
    for key in (
        "phase",
        "validation_readiness_registry_ready",
        "validation_layer_count",
        "layer_mismatch_count",
        "retrospective_diagnostic_distinguished_from_validation",
        "historical_accuracy_validation_not_started",
        "economic_validation_not_started",
        "prospective_validation_not_started",
        "holdout_registered",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "production_behavior_change_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
