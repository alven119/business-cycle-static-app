"""Print a concise portfolio backtest dry-run contract summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    PortfolioBacktestDryRunContractError,
    load_portfolio_backtest_dry_run_contract,
    summarize_portfolio_backtest_dry_run_contract,
)

DEFAULT_CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_dry_run_contract.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show portfolio backtest dry-run contract summary.")
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Portfolio backtest dry-run contract YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_portfolio_backtest_dry_run_contract(args.contract)
        summary = summarize_portfolio_backtest_dry_run_contract(contract)
    except PortfolioBacktestDryRunContractError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"allowed_scope_count={summary['allowed_scope_count']}")
    print(f"disallowed_scope_count={summary['disallowed_scope_count']}")
    print(f"prohibited_output_field_count={summary['prohibited_output_field_count']}")
    print(f"stdout_required_line_count={summary['stdout_required_line_count']}")
    print(f"compute_returns_allowed={str(summary['compute_returns_allowed']).lower()}")
    print(f"allocation_output_allowed={str(summary['allocation_output_allowed']).lower()}")
    print(f"trade_signal_output_allowed={str(summary['trade_signal_output_allowed']).lower()}")
    print(
        "data_backtests_output_allowed="
        f"{str(summary['data_backtests_output_allowed']).lower()}"
    )
    print(f"public_output_allowed={str(summary['public_output_allowed']).lower()}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
