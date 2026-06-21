"""Print a concise backtest result caveat policy summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    BacktestResultCaveatPolicyError,
    load_backtest_result_caveat_policy,
    summarize_backtest_result_caveat_policy,
)

DEFAULT_POLICY_PATH = Path("specs/portfolio/backtest_result_caveat_policy.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show backtest result caveat policy summary.")
    parser.add_argument(
        "--policy",
        default=str(DEFAULT_POLICY_PATH),
        help="Backtest result caveat policy YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        policy = load_backtest_result_caveat_policy(args.policy)
        summary = summarize_backtest_result_caveat_policy(policy)
    except BacktestResultCaveatPolicyError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"required_global_caveat_count={summary['required_global_caveat_count']}")
    print(f"contextual_caveat_count={summary['contextual_caveat_count']}")
    print(f"prohibited_text_pattern_count={summary['prohibited_text_pattern_count']}")
    print(f"prohibited_result_field_count={summary['prohibited_result_field_count']}")
    print(f"future_validation_rule_count={summary['future_validation_rule_count']}")
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
    print(
        "create_output_directories_allowed="
        f"{str(summary['create_output_directories_allowed']).lower()}"
    )
    print(f"produce_allocation_allowed={str(summary['produce_allocation_allowed']).lower()}")
    print(f"produce_trade_signal_allowed={str(summary['produce_trade_signal_allowed']).lower()}")
    print(f"caveats_visible_before_metrics={str(summary['caveats_visible_before_metrics']).lower()}")
    print(f"phase_9a4_closure_status={summary['phase_9a4_closure_status']}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
