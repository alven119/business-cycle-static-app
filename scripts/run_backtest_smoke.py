"""Run limited smoke backtests across historical scenarios."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import BacktestScenarioError, BacktestSmokeError, run_backtest_smoke  # noqa: E402

DEFAULT_SCENARIO_PATH = Path("specs/backtests/scenarios.yaml")
DEFAULT_OUTPUT_DIR = Path("data/backtests")
DEFAULT_OUTPUT = Path("data/backtests/smoke_summary.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run limited smoke backtests across scenarios.")
    parser.add_argument(
        "--scenario-path",
        default=str(DEFAULT_SCENARIO_PATH),
        help="Backtest scenario YAML path.",
    )
    parser.add_argument("--scenario-id", help="Run only one scenario id.")
    parser.add_argument(
        "--max-periods",
        type=int,
        default=24,
        help="Limit monthly periods per scenario.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Root directory for generated backtest outputs.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Smoke summary JSON output path.",
    )
    parser.add_argument(
        "--transition-controls",
        help="Optional experimental transition controls YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_backtest_smoke(
            catalog_path=args.scenario_path,
            output_dir=args.output_dir,
            output_path=args.output,
            max_periods=args.max_periods,
            scenario_id=args.scenario_id,
            transition_controls_path=args.transition_controls,
        )
    except (BacktestScenarioError, BacktestSmokeError, ValueError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    aggregate = summary["aggregate"]
    print(
        "backtest_smoke "
        f"scenario_count={summary['scenario_count']} "
        f"max_periods={summary['max_periods']} "
        f"total_plausibility_warning_count={aggregate['total_plausibility_warning_count']} "
        "scenario_with_plausibility_warnings_count="
        f"{aggregate['scenario_with_plausibility_warnings_count']} "
        f"output={summary['output_path']}"
    )

    scenario_execution_failures = sum(1 for item in summary["scenarios"] if "scenario_failure" in item)
    if scenario_execution_failures > 0:
        print(f"scenario_execution_failure_count={scenario_execution_failures}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
