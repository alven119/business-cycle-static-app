"""Validate backtest result safety validator fixtures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    BacktestResultSafetyValidatorContractError,
    load_backtest_result_safety_validator_contract,
    load_backtest_result_safety_validator_fixtures,
    validate_backtest_result_safety_validator_fixtures,
)

DEFAULT_CONTRACT_PATH = Path("specs/portfolio/backtest_result_safety_validator_contract.yaml")
DEFAULT_FIXTURES_PATH = Path("specs/portfolio/backtest_result_safety_validator_fixtures.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate backtest result safety validator fixtures."
    )
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Backtest result safety validator contract YAML path.",
    )
    parser.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURES_PATH),
        help="Backtest result safety validator fixtures YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_backtest_result_safety_validator_contract(args.contract)
        fixtures = load_backtest_result_safety_validator_fixtures(args.fixtures)
        summary = validate_backtest_result_safety_validator_fixtures(
            fixtures,
            contract,
        )
    except BacktestResultSafetyValidatorContractError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"contract_version={summary.contract_version}")
    print(f"fixtures_version={summary.fixtures_version}")
    print(f"valid_result_fixture_count={summary.valid_result_fixture_count}")
    print(f"invalid_result_fixture_count={summary.invalid_result_fixture_count}")
    print(f"valid_pass_count={summary.valid_pass_count}")
    print(f"invalid_rejected_count={summary.invalid_rejected_count}")
    print(f"unexpected_valid_failures={summary.unexpected_valid_failures}")
    print(f"unexpected_invalid_passes={summary.unexpected_invalid_passes}")
    print(f"expected_error_mismatches={summary.expected_error_mismatches}")
    print(f"public_output_written={str(summary.public_output_written).lower()}")
    print(
        "data_backtests_output_written="
        f"{str(summary.data_backtests_output_written).lower()}"
    )
    print(f"output_written={str(summary.output_written).lower()}")
    print(
        "allocation_output_generated="
        f"{str(summary.allocation_output_generated).lower()}"
    )
    print(f"trade_signal_generated={str(summary.trade_signal_generated).lower()}")
    print(f"result={summary.result}")
    return 0 if summary.result == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
