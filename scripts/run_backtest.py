"""Run a historical backtest scenario."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BacktestRunConfig,
    BacktestScenarioError,
    generate_monthly_periods,
    get_scenario,
    load_backtest_scenario_catalog,
    run_backtest,
)

DEFAULT_SCENARIO_PATH = Path("specs/backtests/scenarios.yaml")
DEFAULT_OUTPUT_DIR = Path("data/backtests")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a historical backtest scenario.")
    parser.add_argument("--scenario-id", required=True, help="Backtest scenario id.")
    parser.add_argument(
        "--scenario-path",
        default=str(DEFAULT_SCENARIO_PATH),
        help="Backtest scenario YAML path.",
    )
    parser.add_argument("--max-periods", type=int, help="Limit monthly periods for smoke tests.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Root directory for generated backtest outputs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned as-of dates without writing output.",
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
        catalog = load_backtest_scenario_catalog(args.scenario_path)
        scenario = get_scenario(catalog, args.scenario_id)
    except BacktestScenarioError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    periods = generate_monthly_periods(
        scenario.window_start,
        scenario.window_end,
        max_periods=args.max_periods,
    )
    output_path = Path(args.output_dir) / scenario.scenario_id / "timeline.json"
    transition_controls_path = Path(args.transition_controls) if args.transition_controls else None
    if transition_controls_path is not None and not transition_controls_path.exists():
        parser.exit(status=1, message=f"error: transition controls config does not exist: {transition_controls_path}\n")
    if args.dry_run:
        print(
            "dry_run "
            f"scenario_id={scenario.scenario_id} period_count={len(periods)} "
            f"first_as_of={periods[0] if periods else 'none'} "
            f"last_as_of={periods[-1] if periods else 'none'} output={output_path}"
        )
        for period in periods:
            print(f"as_of={period}")
        return 0

    config = BacktestRunConfig(
        scenario_id=scenario.scenario_id,
        scenario=scenario,
        output_dir=Path(args.output_dir),
        max_periods=args.max_periods,
        data_mode=scenario.data_mode,
        transition_controls_path=transition_controls_path,
    )
    result = run_backtest(config)
    first_as_of = result.timeline[0].as_of if result.timeline else "none"
    last_as_of = result.timeline[-1].as_of if result.timeline else "none"
    print(
        "backtest "
        f"scenario_id={result.scenario_id} period_count={result.period_count} "
        f"first_as_of={first_as_of} last_as_of={last_as_of} output={result.output_path}"
    )
    if result.failures:
        print(
            "warning "
            "one or more periods recorded failures; confirm data/raw/fred cache is available."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
