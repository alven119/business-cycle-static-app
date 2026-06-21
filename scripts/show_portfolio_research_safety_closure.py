"""Print a concise portfolio research safety closure summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    PortfolioResearchSafetyClosureError,
    load_portfolio_research_safety_closure,
    summarize_portfolio_research_safety_closure,
)

DEFAULT_CLOSURE_PATH = Path("specs/portfolio/portfolio_research_safety_closure.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show portfolio research safety closure summary.")
    parser.add_argument(
        "--closure",
        default=str(DEFAULT_CLOSURE_PATH),
        help="Portfolio research safety closure YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        closure = load_portfolio_research_safety_closure(args.closure)
        summary = summarize_portfolio_research_safety_closure(closure)
    except PortfolioResearchSafetyClosureError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"artifact_count={summary['artifact_count']}")
    print(f"validator_count={summary['validator_count']}")
    print(f"active_blocker_count={summary['active_blocker_count']}")
    print(f"required_before_real_backtest_count={summary['required_before_real_backtest_count']}")
    print(f"phase_8_closure_status={summary['phase_8_closure_status']}")
    print(f"research_only={str(summary['research_only']).lower()}")
    print(f"structural_dry_run_only={str(summary['structural_dry_run_only']).lower()}")
    print(f"formal_backtest_executed={str(summary['formal_backtest_executed']).lower()}")
    print(f"performance_metrics_computed={str(summary['performance_metrics_computed']).lower()}")
    print(f"allocation_output_generated={str(summary['allocation_output_generated']).lower()}")
    print(f"trade_signal_generated={str(summary['trade_signal_generated']).lower()}")
    print(
        "data_backtests_output_written="
        f"{str(summary['data_backtests_output_written']).lower()}"
    )
    print(f"public_output_written={str(summary['public_output_written']).lower()}")
    print(f"live_recommendation_allowed={str(summary['live_recommendation_allowed']).lower()}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
