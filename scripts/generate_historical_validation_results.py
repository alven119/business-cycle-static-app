#!/usr/bin/env python
from __future__ import annotations

import argparse

from business_cycle.validation.historical_validation_results import (
    build_historical_validation_results,
    write_historical_validation_results,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run = build_historical_validation_results()
    write_result = write_historical_validation_results(run, output=args.output)
    for key in (
        "phase",
        "historical_validation_result_runtime_ready",
        "scenario_count",
        "comparable_scenario_count",
        "non_comparable_scenario_count",
        "historical_validation_result_artifact_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "metric_computation_scope",
        "economic_performance_metric_count",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prohibited_result_field_count",
    ):
        value = run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")
    print(
        "historical_validation_result_written="
        f"{str(write_result['historical_validation_result_written']).lower()}"
    )


if __name__ == "__main__":
    main()
