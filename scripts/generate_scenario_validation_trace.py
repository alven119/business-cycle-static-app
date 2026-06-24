#!/usr/bin/env python
from __future__ import annotations

import argparse

from business_cycle.validation.scenario_validation_trace import (
    build_scenario_validation_trace,
    write_scenario_validation_trace,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    trace_run = build_scenario_validation_trace()
    write_result = write_scenario_validation_trace(trace_run, output=args.output)
    for key in (
        "phase",
        "scenario_validation_trace_contract_ready",
        "scenario_validation_trace_runtime_ready",
        "scenario_count",
        "scenario_trace_count",
        "prohibited_trace_field_count",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "metric_computation_scope",
        "backtest_execution_enabled",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
    ):
        value = trace_run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")
    print(
        "scenario_validation_trace_written="
        f"{str(write_result['scenario_validation_trace_written']).lower()}"
    )


if __name__ == "__main__":
    main()
