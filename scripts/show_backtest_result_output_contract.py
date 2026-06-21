"""Print a concise backtest result output contract summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    BacktestResultOutputContractError,
    load_backtest_result_output_contract,
    summarize_backtest_result_output_contract,
)

DEFAULT_CONTRACT_PATH = Path("specs/portfolio/backtest_result_output_contract.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show backtest result output contract summary.")
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Backtest result output contract YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_backtest_result_output_contract(args.contract)
        summary = summarize_backtest_result_output_contract(contract)
    except BacktestResultOutputContractError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"required_result_field_count={summary['required_result_field_count']}")
    print(f"future_metric_field_count={summary['future_metric_field_count']}")
    print(f"prohibited_result_field_count={summary['prohibited_result_field_count']}")
    print(
        "prohibited_auto_write_location_count="
        f"{summary['prohibited_auto_write_location_count']}"
    )
    print(
        "produce_backtest_results_allowed="
        f"{str(summary['produce_backtest_results_allowed']).lower()}"
    )
    print(f"compute_metric_values_allowed={str(summary['compute_metric_values_allowed']).lower()}")
    print(f"write_result_files_allowed={str(summary['write_result_files_allowed']).lower()}")
    print(
        "write_data_backtests_output_allowed="
        f"{str(summary['write_data_backtests_output_allowed']).lower()}"
    )
    print(f"write_public_output_allowed={str(summary['write_public_output_allowed']).lower()}")
    print(f"produce_allocation_allowed={str(summary['produce_allocation_allowed']).lower()}")
    print(f"produce_trade_signal_allowed={str(summary['produce_trade_signal_allowed']).lower()}")
    print(f"metric_values_allowed_now={str(summary['metric_values_allowed_now']).lower()}")
    print(f"auto_write_allowed_now={str(summary['auto_write_allowed_now']).lower()}")
    print(f"phase_9a1_closure_status={summary['phase_9a1_closure_status']}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
