"""Print a concise backtest result writer contract summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    BacktestResultWriterContractError,
    load_backtest_result_writer_contract,
    summarize_backtest_result_writer_contract,
)

DEFAULT_CONTRACT_PATH = Path("specs/portfolio/backtest_result_writer_contract.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show backtest result writer contract summary."
    )
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Backtest result writer contract YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_backtest_result_writer_contract(args.contract)
        summary = summarize_backtest_result_writer_contract(contract)
    except BacktestResultWriterContractError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"prohibited_write_location_count={summary['prohibited_write_location_count']}")
    print(f"pre_write_validation_count={summary['pre_write_validation_count']}")
    print(f"writer_status_field_count={summary['writer_status_field_count']}")
    print(f"prohibited_result_field_count={summary['prohibited_result_field_count']}")
    print(
        "explicit_user_command_required="
        f"{str(summary['explicit_user_command_required']).lower()}"
    )
    print(f"automatic_write_allowed={str(summary['automatic_write_allowed']).lower()}")
    print(
        "implement_writer_runtime_allowed="
        f"{str(summary['implement_writer_runtime_allowed']).lower()}"
    )
    print(f"write_result_files_allowed={str(summary['write_result_files_allowed']).lower()}")
    print(
        "create_output_directories_allowed="
        f"{str(summary['create_output_directories_allowed']).lower()}"
    )
    print(
        "write_data_backtests_output_allowed="
        f"{str(summary['write_data_backtests_output_allowed']).lower()}"
    )
    print(f"write_public_output_allowed={str(summary['write_public_output_allowed']).lower()}")
    print(f"write_docs_output_allowed={str(summary['write_docs_output_allowed']).lower()}")
    print(
        "write_dashboard_output_allowed="
        f"{str(summary['write_dashboard_output_allowed']).lower()}"
    )
    print(
        "write_github_pages_output_allowed="
        f"{str(summary['write_github_pages_output_allowed']).lower()}"
    )
    print(f"execute_backtest_allowed={str(summary['execute_backtest_allowed']).lower()}")
    print(f"compute_metric_values_allowed={str(summary['compute_metric_values_allowed']).lower()}")
    print(f"produce_allocation_allowed={str(summary['produce_allocation_allowed']).lower()}")
    print(f"produce_trade_signal_allowed={str(summary['produce_trade_signal_allowed']).lower()}")
    print(f"writer_runtime_allowed_now={str(summary['writer_runtime_allowed_now']).lower()}")
    print(
        "result_file_write_allowed_now="
        f"{str(summary['result_file_write_allowed_now']).lower()}"
    )
    print(
        "output_directory_creation_allowed_now="
        f"{str(summary['output_directory_creation_allowed_now']).lower()}"
    )
    print(
        "data_backtests_write_allowed_now="
        f"{str(summary['data_backtests_write_allowed_now']).lower()}"
    )
    print(f"public_write_allowed_now={str(summary['public_write_allowed_now']).lower()}")
    print(f"phase_9a7_closure_status={summary['phase_9a7_closure_status']}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
