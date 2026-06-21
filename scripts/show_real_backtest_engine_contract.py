"""Print a concise real backtest engine contract summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    RealBacktestEngineContractError,
    load_real_backtest_engine_contract,
    summarize_real_backtest_engine_contract,
)

DEFAULT_CONTRACT_PATH = Path("specs/portfolio/real_backtest_engine_contract.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show real backtest engine contract summary.")
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Real backtest engine contract YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_real_backtest_engine_contract(args.contract)
        summary = summarize_real_backtest_engine_contract(contract)
    except RealBacktestEngineContractError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"input_contract_count={summary['input_contract_count']}")
    print(f"future_dependency_contract_count={summary['future_dependency_contract_count']}")
    print(f"engine_stage_count={summary['engine_stage_count']}")
    print(f"prohibited_output_count={summary['prohibited_output_count']}")
    print(
        "prohibited_auto_write_location_count="
        f"{summary['prohibited_auto_write_location_count']}"
    )
    print(
        "implement_engine_runtime_allowed="
        f"{str(summary['implement_engine_runtime_allowed']).lower()}"
    )
    print(f"execute_backtest_allowed={str(summary['execute_backtest_allowed']).lower()}")
    print(
        "compute_performance_metrics_allowed="
        f"{str(summary['compute_performance_metrics_allowed']).lower()}"
    )
    print(
        "produce_backtest_results_allowed="
        f"{str(summary['produce_backtest_results_allowed']).lower()}"
    )
    print(
        "write_data_backtests_output_allowed="
        f"{str(summary['write_data_backtests_output_allowed']).lower()}"
    )
    print(f"write_public_output_allowed={str(summary['write_public_output_allowed']).lower()}")
    print(f"produce_allocation_allowed={str(summary['produce_allocation_allowed']).lower()}")
    print(f"produce_trade_signal_allowed={str(summary['produce_trade_signal_allowed']).lower()}")
    print(f"phase_9a_closure_status={summary['phase_9a_closure_status']}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
