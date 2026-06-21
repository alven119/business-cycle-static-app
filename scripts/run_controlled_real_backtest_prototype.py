"""Run controlled real backtest prototype from fixture data in memory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    ControlledRealBacktestPrototypeError,
    load_controlled_real_backtest_prototype_fixtures,
    run_controlled_real_backtest_prototype,
    summarize_controlled_real_backtest_prototype,
)

DEFAULT_FIXTURES_PATH = Path(
    "specs/portfolio/controlled_real_backtest_prototype_fixtures.yaml"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run controlled real backtest prototype in memory."
    )
    parser.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURES_PATH),
        help="Controlled real backtest prototype fixtures YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        fixtures = load_controlled_real_backtest_prototype_fixtures(args.fixtures)
        run_result = run_controlled_real_backtest_prototype(fixtures)
        summary = summarize_controlled_real_backtest_prototype(run_result)
    except ControlledRealBacktestPrototypeError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"case_count={summary['case_count']}")
    print(f"prototype_run_count={summary['prototype_run_count']}")
    print(f"computed_metric_count={summary['computed_metric_count']}")
    print(f"required_metric_count={summary['required_metric_count']}")
    print(f"in_memory_only={str(summary['in_memory_only']).lower()}")
    print(
        "controlled_metric_computation_allowed="
        f"{str(summary['controlled_metric_computation_allowed']).lower()}"
    )
    print(f"result_file_written={str(summary['result_file_written']).lower()}")
    print(
        "data_backtests_output_written="
        f"{str(summary['data_backtests_output_written']).lower()}"
    )
    print(f"public_output_written={str(summary['public_output_written']).lower()}")
    print(f"output_directory_created={str(summary['output_directory_created']).lower()}")
    print(
        "allocation_output_generated="
        f"{str(summary['allocation_output_generated']).lower()}"
    )
    print(f"trade_signal_generated={str(summary['trade_signal_generated']).lower()}")
    print(
        "live_recommendation_generated="
        f"{str(summary['live_recommendation_generated']).lower()}"
    )
    print(f"dashboard_integration={str(summary['dashboard_integration']).lower()}")
    print(f"result={summary['result']}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
