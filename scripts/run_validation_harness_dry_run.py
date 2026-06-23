from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_cycle.validation.validation_harness import (
    run_validation_harness_dry_run,
    summarize_validation_harness_dry_run,
)


PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Phase 16 validation harness synthetic dry-run."
    )
    parser.add_argument("--fixture-mode", required=True, choices=("synthetic",))
    parser.add_argument("--output")
    args = parser.parse_args()

    dry_run = run_validation_harness_dry_run(fixture_mode=args.fixture_mode)
    if args.output:
        output_path = Path(args.output)
        _reject_prohibited_output(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(dry_run, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    summary = summarize_validation_harness_dry_run()
    for key in (
        "phase",
        "validation_harness_contract_ready",
        "validation_harness_runtime_ready",
        "validation_artifact_contract_ready",
        "synthetic_fixture_count",
        "fixture_pass_count",
        "synthetic_dry_run_executed",
        "real_historical_validation_executed",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "metric_computation_enabled",
        "backtest_execution_enabled",
        "holdout_registered",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "forbidden_output_field_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


def _reject_prohibited_output(output_path: Path) -> None:
    normalized = output_path if output_path.is_absolute() else Path.cwd() / output_path
    for root in PROHIBITED_OUTPUT_ROOTS:
        root_path = Path.cwd() / root
        if normalized.resolve().is_relative_to(root_path.resolve()):
            raise SystemExit(f"refusing prohibited output path: {output_path}")


if __name__ == "__main__":
    main()
