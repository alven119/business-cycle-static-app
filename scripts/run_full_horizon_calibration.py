"""Run full-horizon calibration experiment and acceptance review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BacktestScenarioError,
    CalibrationExperimentError,
    run_full_horizon_calibration,
)

DEFAULT_SCENARIO_PATH = Path("specs/backtests/scenarios.yaml")
DEFAULT_CONTROLS_PATH = Path("specs/backtests/transition_controls_enabled_experiment.yaml")
DEFAULT_OUTPUT_DIR = Path("data/backtests/calibration")
DEFAULT_WINDOWS_PATH = Path("specs/backtests/calibration_acceptance_windows.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a full-horizon calibration experiment.")
    parser.add_argument("--experiment-id", required=True, help="Experiment id used under output-dir.")
    parser.add_argument("--scenario-path", default=str(DEFAULT_SCENARIO_PATH), help="Backtest scenario YAML path.")
    parser.add_argument("--controls", default=str(DEFAULT_CONTROLS_PATH), help="Enabled transition controls YAML path.")
    parser.add_argument("--scenario-id", help="Run only one scenario id.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Calibration output root.")
    parser.add_argument("--windows", default=str(DEFAULT_WINDOWS_PATH), help="Acceptance windows YAML path.")
    parser.add_argument("--reuse-existing", action="store_true", help="Reuse complete existing generated outputs.")
    parser.add_argument("--force", action="store_true", help="Recompute even when reusable outputs exist.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_full_horizon_calibration(
            experiment_id=args.experiment_id,
            catalog_path=args.scenario_path,
            controls_config_path=args.controls,
            output_dir=args.output_dir,
            scenario_id=args.scenario_id,
            windows_path=args.windows,
            reuse_existing=args.reuse_existing,
            force=args.force,
        )
        review = json.loads(Path(summary["acceptance_review_path"]).read_text(encoding="utf-8"))
    except (BacktestScenarioError, CalibrationExperimentError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    aggregate = review["aggregate"]
    print(
        "full_horizon_calibration "
        f"experiment_id={summary['experiment_id']} "
        f"scenario_count={review['scenario_count']} "
        f"pass_count={aggregate['pass_count']} "
        f"warning_count={aggregate['warning_count']} "
        f"fail_count={aggregate['fail_count']} "
        f"needs_longer_horizon_count={aggregate['needs_longer_horizon_count']} "
        f"early_false_recession_count={aggregate['early_false_recession_count']} "
        f"reused_output_count={summary.get('reuse', {}).get('reused_output_count', 0)} "
        f"recomputed_output_count={summary.get('reuse', {}).get('recomputed_output_count', 0)} "
        f"output={summary['acceptance_review_path']}"
    )
    return 1 if summary["aggregate"]["scenario_with_failures_count"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
