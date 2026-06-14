"""List configured historical backtest scenarios."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BacktestScenario,
    BacktestScenarioError,
    get_scenario,
    load_backtest_scenario_catalog,
)

DEFAULT_SCENARIO_PATH = Path("specs/backtests/scenarios.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List configured backtest scenarios.")
    parser.add_argument(
        "--scenario-path",
        default=str(DEFAULT_SCENARIO_PATH),
        help="Backtest scenario YAML path.",
    )
    parser.add_argument("--scenario-id", help="Only show one scenario in detail.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        catalog = load_backtest_scenario_catalog(args.scenario_path)
        scenarios = (
            [get_scenario(catalog, args.scenario_id)] if args.scenario_id else catalog.scenarios
        )
    except BacktestScenarioError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    for scenario in scenarios:
        print(_summary_line(scenario))
        if args.scenario_id:
            print(f"display_name_en={scenario.display_name_en}")
            print("expected_focus_zh:")
            for item in scenario.expected_focus_zh:
                print(f"- {item}")
            print(f"benchmark_notes_zh={scenario.benchmark_notes_zh}")
    return 0


def _summary_line(scenario: BacktestScenario) -> str:
    return (
        f"scenario_id={scenario.scenario_id} "
        f"display_name_zh={scenario.display_name_zh} "
        f"window_start={scenario.window_start.isoformat()} "
        f"window_end={scenario.window_end.isoformat()} "
        f"focus_transition={scenario.focus_transition} "
        f"baseline_phase_id={scenario.baseline_phase_id} "
        f"data_mode={scenario.data_mode}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
