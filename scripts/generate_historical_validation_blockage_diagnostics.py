#!/usr/bin/env python
from __future__ import annotations

import argparse

from business_cycle.validation.historical_validation_blockage_diagnostics import (
    build_historical_validation_blockage_diagnostics,
    write_historical_validation_blockage_diagnostics,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    diagnostic_run = build_historical_validation_blockage_diagnostics()
    write_result = write_historical_validation_blockage_diagnostics(
        diagnostic_run,
        output=args.output,
    )
    for key in (
        "phase",
        "historical_validation_blockage_diagnostics_contract_ready",
        "historical_validation_blockage_diagnostics_runtime_ready",
        "scenario_count",
        "scenario_trace_count",
        "blockage_diagnostic_scenario_count",
        "comparable_scenario_count",
        "non_comparable_scenario_count",
        "abstained_scenario_count",
        "blocked_scenario_count",
        "taxonomy_mismatch_count",
        "blockage_reason_summary_ready",
        "remediation_plan_registry_ready",
        "remediation_action_executed",
        "rule_modified_count",
        "mapping_rule_modified_count",
        "threshold_modified_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "metric_computation_scope",
        "backtest_execution_enabled",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prohibited_artifact_field_count",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "forbidden_repo_output_count",
    ):
        value = diagnostic_run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")
    print(
        "blockage_diagnostics_artifact_written="
        f"{str(write_result['blockage_diagnostics_artifact_written']).lower()}"
    )


if __name__ == "__main__":
    main()
