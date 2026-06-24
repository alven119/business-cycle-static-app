#!/usr/bin/env python
from __future__ import annotations

import argparse

from business_cycle.validation.historical_accuracy_metrics import (
    compute_historical_accuracy_metrics,
    write_historical_accuracy_metrics,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    metric_run = compute_historical_accuracy_metrics()
    write_result = write_historical_accuracy_metrics(metric_run, output=args.output)
    for key in (
        "phase",
        "historical_accuracy_metric_artifact_contract_ready",
        "historical_accuracy_metric_runtime_ready",
        "preregistered_metric_registry_used",
        "scenario_count",
        "label_comparison_artifact_count",
        "comparable_scenario_count",
        "non_comparable_scenario_count",
        "abstained_scenario_count",
        "blocked_scenario_count",
        "taxonomy_mismatch_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "metric_computation_scope",
        "backtest_execution_enabled",
        "label_used_by_runtime_count",
        "mapping_rule_modified_after_comparison_count",
        "threshold_modified_after_metric_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prohibited_metric_field_count",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "forbidden_repo_output_count",
    ):
        value = metric_run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")
    print(
        "historical_accuracy_metric_artifact_written="
        f"{str(write_result['historical_accuracy_metric_artifact_written']).lower()}"
    )


if __name__ == "__main__":
    main()
