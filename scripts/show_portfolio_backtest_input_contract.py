"""Print a concise portfolio backtest input contract summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    PortfolioBacktestContractError,
    load_portfolio_backtest_input_contract,
    load_portfolio_backtest_scenario_mapping,
    summarize_portfolio_backtest_input_contract,
)

DEFAULT_CONTRACT_PATH = Path("specs/portfolio/portfolio_backtest_input_contract.yaml")
DEFAULT_MAPPING_PATH = Path("specs/portfolio/portfolio_backtest_scenario_mapping.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show portfolio backtest input contract summary.")
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Portfolio backtest input contract YAML path.",
    )
    parser.add_argument(
        "--mapping",
        default=str(DEFAULT_MAPPING_PATH),
        help="Portfolio backtest scenario mapping YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_portfolio_backtest_input_contract(args.contract)
        mapping = load_portfolio_backtest_scenario_mapping(args.mapping)
        summary = summarize_portfolio_backtest_input_contract(contract, mapping)
    except PortfolioBacktestContractError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"allowed_policy_template_count={summary['allowed_policy_template_count']}")
    print(f"allowed_scenario_count={summary['allowed_scenario_count']}")
    print(f"mapped_scenario_count={summary['mapped_scenario_count']}")
    print(f"required_metric_count={summary['required_metric_count']}")
    print(f"prohibited_output_count={summary['prohibited_output_count']}")
    print(
        "live_allocation_output_allowed="
        f"{str(summary['live_allocation_output_allowed']).lower()}"
    )
    print(
        "trade_signal_output_allowed="
        f"{str(summary['trade_signal_output_allowed']).lower()}"
    )
    print(
        "public_dashboard_output_allowed="
        f"{str(summary['public_dashboard_output_allowed']).lower()}"
    )
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
