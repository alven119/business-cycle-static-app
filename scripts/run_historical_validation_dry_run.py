from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.validation.historical_validation_dry_run import (
    run_historical_validation_dry_run,
    summarize_historical_validation_dry_run,
)
from business_cycle.validation.historical_validation_result_writer import (
    write_historical_validation_dry_run_results,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Phase 20 label-blind historical validation dry-run."
    )
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    dry_run = run_historical_validation_dry_run()
    write_historical_validation_dry_run_results(
        dry_run,
        output_dir=Path(args.output_dir),
    )
    summary = summarize_historical_validation_dry_run()
    for key in (
        "phase",
        "historical_validation_dry_run_contract_ready",
        "historical_validation_dry_run_executed",
        "scenario_count",
        "scenario_dry_run_result_count",
        "locked_execution_plan_used",
        "label_blind_execution_verified",
        "label_used_by_runtime_count",
        "model_execution_count",
        "real_historical_validation_executed",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "holdout_registered",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prohibited_result_field_count",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
