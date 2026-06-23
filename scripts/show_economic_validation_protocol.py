from __future__ import annotations

from business_cycle.validation.economic_validation_protocol import (
    summarize_economic_validation_protocol,
)


def main() -> None:
    summary = summarize_economic_validation_protocol()
    for key in (
        "phase",
        "protocol_id",
        "protocol_version",
        "economic_validation_protocol_ready",
        "validation_layer_count",
        "missing_required_field_count",
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
        "disabled_runtime_guards_hold",
        "backtest_or_metric_execution_count",
        "validation_execution_started_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
