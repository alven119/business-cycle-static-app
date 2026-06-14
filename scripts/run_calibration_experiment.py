"""Run calibration experiments comparing baseline and transition controls."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BacktestScenarioError,
    CalibrationExperimentError,
    run_calibration_experiment,
)

DEFAULT_SCENARIO_PATH = Path("specs/backtests/scenarios.yaml")
DEFAULT_CONTROLS_PATH = Path("specs/backtests/transition_controls_enabled_experiment.yaml")
DEFAULT_OUTPUT_DIR = Path("data/backtests/calibration")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a calibration experiment.")
    parser.add_argument("--experiment-id", required=True, help="Experiment id used under output-dir.")
    parser.add_argument(
        "--scenario-path",
        default=str(DEFAULT_SCENARIO_PATH),
        help="Backtest scenario YAML path.",
    )
    parser.add_argument(
        "--controls",
        default=str(DEFAULT_CONTROLS_PATH),
        help="Enabled transition controls YAML path.",
    )
    parser.add_argument("--scenario-id", help="Run only one scenario id.")
    parser.add_argument("--max-periods", type=int, help="Limit monthly periods per scenario.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Root directory for calibration experiment outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_calibration_experiment(
            experiment_id=args.experiment_id,
            catalog_path=args.scenario_path,
            controls_config_path=args.controls,
            output_dir=args.output_dir,
            max_periods=args.max_periods,
            scenario_id=args.scenario_id,
        )
    except (BacktestScenarioError, CalibrationExperimentError, ValueError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    aggregate = summary["aggregate"]
    print(
        "calibration_experiment "
        f"experiment_id={summary['experiment_id']} "
        f"scenario_count={summary['scenario_count']} "
        f"baseline_total_plausibility_warning_count={aggregate['baseline_total_plausibility_warning_count']} "
        f"experiment_total_plausibility_warning_count={aggregate['experiment_total_plausibility_warning_count']} "
        f"delta_total_plausibility_warning_count={aggregate['delta_total_plausibility_warning_count']} "
        f"scenario_improved_count={aggregate['scenario_improved_count']} "
        f"scenario_regressed_count={aggregate['scenario_regressed_count']} "
        f"output={summary['output_path']}"
    )
    return 1 if aggregate["scenario_with_failures_count"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
