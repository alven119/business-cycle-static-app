"""Run portfolio backtest structural dry-run and print stdout-only summary."""

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
    load_portfolio_backtest_input_contract,
    load_portfolio_backtest_input_fixtures,
    load_portfolio_backtest_scenario_mapping,
    run_portfolio_backtest_structural_dry_run,
)

DEFAULT_CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_dry_run_contract.yaml")
DEFAULT_INPUT_CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_input_contract.yaml")
DEFAULT_MAPPING_PATH = Path("specs/portfolio/portfolio_backtest_scenario_mapping.yaml")
DEFAULT_FIXTURES_PATH = Path("specs/portfolio/portfolio_backtest_input_fixtures.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run stdout-only portfolio structural dry-run.")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT_PATH))
    parser.add_argument("--input-contract", default=str(DEFAULT_INPUT_CONTRACT_PATH))
    parser.add_argument("--mapping", default=str(DEFAULT_MAPPING_PATH))
    parser.add_argument("--fixtures", default=str(DEFAULT_FIXTURES_PATH))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        dry_run_contract = load_portfolio_backtest_dry_run_contract(args.contract)
        input_contract = load_portfolio_backtest_input_contract(args.input_contract)
        mapping = load_portfolio_backtest_scenario_mapping(args.mapping)
        fixtures = load_portfolio_backtest_input_fixtures(args.fixtures)
        report = run_portfolio_backtest_structural_dry_run(
            dry_run_contract,
            input_contract,
            mapping,
            fixtures,
        )
    except PortfolioBacktestDryRunContractError as exc:
        print("result=failed")
        parser.exit(status=1, message=f"error: {exc}\n")
    except Exception as exc:
        print("result=failed")
        parser.exit(status=1, message=f"error: {exc}\n")

    summary = report["summary"]
    print(f"dry_run_count={summary['dry_run_count']}")
    print(f"valid_dry_run_count={summary['valid_dry_run_count']}")
    print(f"invalid_dry_run_count={summary['invalid_dry_run_count']}")
    print(f"scenario_count={summary['scenario_count']}")
    print(f"policy_template_count={summary['policy_template_count']}")
    print(
        "performance_metrics_computed="
        f"{str(summary['performance_metrics_computed']).lower()}"
    )
    print(f"output_written={str(summary['output_written']).lower()}")
    print(
        "data_backtests_output_written="
        f"{str(summary['data_backtests_output_written']).lower()}"
    )
    print(f"public_output_written={str(summary['public_output_written']).lower()}")
    print(
        "allocation_output_generated="
        f"{str(summary['allocation_output_generated']).lower()}"
    )
    print(f"trade_signal_generated={str(summary['trade_signal_generated']).lower()}")
    print(f"result={summary['result']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
