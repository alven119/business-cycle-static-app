from __future__ import annotations

from business_cycle.validation.historical_validation_manifest import (
    summarize_historical_validation_manifest,
)


def main() -> None:
    summary = summarize_historical_validation_manifest()
    for key in (
        "phase",
        "manifest_id",
        "manifest_version",
        "historical_validation_manifest_contract_ready",
        "historical_validation_scenario_manifest_ready",
        "scenario_count",
        "scenario_id_mismatch_count",
        "window_definition_mismatch_count",
        "missing_required_field_count",
        "point_in_time_requirement_present",
        "revised_data_allowed_only_for_declared_comparison",
        "label_provenance_complete",
        "scenario_without_label_provenance_count",
        "label_runtime_usage_prohibited",
        "no_tuning_after_manifest_rule_present",
        "real_historical_validation_executed",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "holdout_registered",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "scenario_execution_started_count",
        "metric_or_backtest_count",
        "candidate_or_current_phase_read_count",
        "disabled_runtime_guards_hold",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
