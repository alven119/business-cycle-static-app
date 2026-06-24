#!/usr/bin/env python
from __future__ import annotations

import argparse

from business_cycle.validation.predicted_label_comparison_artifacts import (
    build_predicted_label_comparison_artifacts,
    write_predicted_label_comparison_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    artifact_run = build_predicted_label_comparison_artifacts()
    write_result = write_predicted_label_comparison_artifacts(
        artifact_run,
        output=args.output,
    )
    for key in (
        "phase",
        "predicted_label_comparison_artifact_contract_ready",
        "predicted_label_comparison_generator_ready",
        "scenario_count",
        "predicted_label_artifact_count",
        "label_comparison_artifact_count",
        "label_comparison_executed",
        "predicted_label_provenance_verified_count",
        "historical_label_provenance_verified_count",
        "mapping_contract_hash_verified",
        "label_used_by_runtime_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prohibited_artifact_field_count",
    ):
        value = artifact_run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")
    print(
        "predicted_label_comparison_artifact_written="
        f"{str(write_result['predicted_label_comparison_artifact_written']).lower()}"
    )


if __name__ == "__main__":
    main()
