"""Run transition attribution smoke diagnostics across scenarios."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import AttributionSmokeError, BacktestScenarioError, run_attribution_smoke  # noqa: E402

DEFAULT_SCENARIO_PATH = Path("specs/backtests/scenarios.yaml")
DEFAULT_OUTPUT_DIR = Path("data/backtests")
DEFAULT_OUTPUT = Path("data/backtests/attribution_summary.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run attribution smoke diagnostics across scenarios.")
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
        help="Limit monthly periods when timeline/report must be generated.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Root directory for generated backtest outputs.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Attribution summary JSON output path.",
    )
    parser.add_argument(
        "--reuse-existing",
        action="store_true",
        help="Use existing timeline/report/attribution outputs instead of rerunning missing steps.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_attribution_smoke(
            catalog_path=args.scenario_path,
            output_dir=args.output_dir,
            output_path=args.output,
            max_periods=args.max_periods,
            scenario_id=args.scenario_id,
            reuse_existing=args.reuse_existing,
        )
    except (AttributionSmokeError, BacktestScenarioError, ValueError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    aggregate = summary["aggregate"]
    print(
        "attribution_smoke "
        f"scenario_count={summary['scenario_count']} "
        f"total_diagnostic_count={aggregate['total_diagnostic_count']} "
        f"scenario_with_failures_count={aggregate['scenario_with_failures_count']} "
        f"attribution_quality_counts={aggregate['attribution_quality_counts']} "
        f"output={summary['output_path']}"
    )
    return 1 if aggregate["scenario_with_failures_count"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
