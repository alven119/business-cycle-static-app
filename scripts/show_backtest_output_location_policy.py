"""Print a concise backtest output location policy summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    BacktestOutputLocationPolicyError,
    load_backtest_output_location_policy,
    summarize_backtest_output_location_policy,
)

DEFAULT_POLICY_PATH = Path("specs/portfolio/backtest_output_location_policy.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show backtest output location policy summary.")
    parser.add_argument(
        "--policy",
        default=str(DEFAULT_POLICY_PATH),
        help="Backtest output location policy YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        policy = load_backtest_output_location_policy(args.policy)
        summary = summarize_backtest_output_location_policy(policy)
    except BacktestOutputLocationPolicyError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(
        "future_controlled_research_path_count="
        f"{summary['future_controlled_research_path_count']}"
    )
    print(
        "prohibited_auto_write_location_count="
        f"{summary['prohibited_auto_write_location_count']}"
    )
    print(f"write_precondition_count={summary['write_precondition_count']}")
    print(f"prohibited_result_field_count={summary['prohibited_result_field_count']}")
    print(f"write_result_files_allowed={str(summary['write_result_files_allowed']).lower()}")
    print(
        "write_data_backtests_output_allowed="
        f"{str(summary['write_data_backtests_output_allowed']).lower()}"
    )
    print(f"write_public_output_allowed={str(summary['write_public_output_allowed']).lower()}")
    print(
        "create_output_directories_allowed="
        f"{str(summary['create_output_directories_allowed']).lower()}"
    )
    print(f"execute_backtest_allowed={str(summary['execute_backtest_allowed']).lower()}")
    print(f"compute_metric_values_allowed={str(summary['compute_metric_values_allowed']).lower()}")
    print(
        "produce_backtest_results_allowed="
        f"{str(summary['produce_backtest_results_allowed']).lower()}"
    )
    print(f"produce_allocation_allowed={str(summary['produce_allocation_allowed']).lower()}")
    print(f"produce_trade_signal_allowed={str(summary['produce_trade_signal_allowed']).lower()}")
    print(f"default_write_allowed_now={str(summary['default_write_allowed_now']).lower()}")
    print(f"public_sync_allowed_now={str(summary['public_sync_allowed_now']).lower()}")
    print(
        "git_track_result_files_allowed_now="
        f"{str(summary['git_track_result_files_allowed_now']).lower()}"
    )
    print(f"phase_9a3_closure_status={summary['phase_9a3_closure_status']}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
