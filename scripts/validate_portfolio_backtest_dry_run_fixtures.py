"""Validate portfolio backtest dry-run output fixtures."""

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
    load_portfolio_backtest_dry_run_fixtures,
    validate_portfolio_backtest_dry_run_fixtures,
)

DEFAULT_CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_dry_run_contract.yaml")
DEFAULT_FIXTURES_PATH = Path("specs/portfolio/portfolio_backtest_dry_run_fixtures.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate portfolio backtest dry-run fixtures.")
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Portfolio backtest dry-run contract YAML path.",
    )
    parser.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURES_PATH),
        help="Portfolio backtest dry-run fixtures YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_portfolio_backtest_dry_run_contract(args.contract)
        fixtures = load_portfolio_backtest_dry_run_fixtures(args.fixtures)
        summary = validate_portfolio_backtest_dry_run_fixtures(fixtures, contract)
    except PortfolioBacktestDryRunContractError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"contract_version={summary.contract_version}")
    print(f"fixtures_version={summary.fixtures_version}")
    print(f"valid_output_count={summary.valid_output_count}")
    print(f"invalid_output_count={summary.invalid_output_count}")
    print(f"valid_pass_count={summary.valid_pass_count}")
    print(f"invalid_rejected_count={summary.invalid_rejected_count}")
    print(f"unexpected_valid_failures={len(summary.unexpected_valid_failures)}")
    print(f"unexpected_invalid_passes={len(summary.unexpected_invalid_passes)}")
    print(f"expected_error_mismatches={len(summary.expected_error_mismatches)}")
    print(f"output_written={str(summary.output_written).lower()}")
    print(
        "data_backtests_output_written="
        f"{str(summary.data_backtests_output_written).lower()}"
    )
    print(f"public_output_written={str(summary.public_output_written).lower()}")
    print(f"allocation_output_generated={str(summary.allocation_output_generated).lower()}")
    print(f"trade_signal_generated={str(summary.trade_signal_generated).lower()}")
    print(f"result={'passed' if summary.passed else 'failed'}")
    if summary.passed:
        return 0
    for failure in summary.unexpected_valid_failures:
        print(f"unexpected_valid_failure={failure['fixture_id']}: {failure['error']}")
    for fixture_id in summary.unexpected_invalid_passes:
        print(f"unexpected_invalid_pass={fixture_id}")
    for mismatch in summary.expected_error_mismatches:
        print(
            "expected_error_mismatch="
            f"{mismatch['fixture_id']}: expected {mismatch['expected']} got {mismatch['error']}"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
