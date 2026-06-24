from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.validation.historical_comparison_coverage_metrics import (
    run_historical_comparison_coverage_metrics,
    summarize_historical_comparison_coverage_metrics,
    write_historical_comparison_coverage_metrics,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Phase 23 comparison coverage metrics without accuracy."
    )
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    metric_run = run_historical_comparison_coverage_metrics()
    write_historical_comparison_coverage_metrics(
        metric_run,
        output_dir=Path(args.output_dir),
    )
    summary = summarize_historical_comparison_coverage_metrics()
    for key in (
        "phase",
        "comparison_coverage_metrics_contract_ready",
        "comparison_coverage_metrics_runtime_ready",
        "scenario_count",
        "label_comparison_artifact_count",
        "label_provenance_verified_count",
        "label_used_by_runtime_count",
        "comparison_coverage_metric_count",
        "metric_computation_enabled",
        "metric_computation_scope",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "prohibited_metric_field_count",
        "predicted_label_output_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "backtest_execution_enabled",
        "holdout_registered",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
