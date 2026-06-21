"""Print a concise real backtest execution readiness closure summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    RealBacktestExecutionReadinessClosureError,
    load_real_backtest_execution_readiness_closure,
    summarize_real_backtest_execution_readiness_closure,
)

DEFAULT_CLOSURE_PATH = Path(
    "specs/portfolio/real_backtest_execution_readiness_closure.yaml"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show real backtest execution readiness closure summary."
    )
    parser.add_argument(
        "--closure",
        default=str(DEFAULT_CLOSURE_PATH),
        help="Real backtest execution readiness closure YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        closure = load_real_backtest_execution_readiness_closure(args.closure)
        summary = summarize_real_backtest_execution_readiness_closure(closure)
    except RealBacktestExecutionReadinessClosureError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"source_artifact_count={summary['source_artifact_count']}")
    print(f"validator_command_count={summary['validator_command_count']}")
    print(
        "remaining_output_write_blocker_count="
        f"{summary['remaining_output_write_blocker_count']}"
    )
    print(
        "phase_9a_contract_stack_complete="
        f"{str(summary['phase_9a_contract_stack_complete']).lower()}"
    )
    print(
        "real_backtest_execution_allowed_now="
        f"{str(summary['real_backtest_execution_allowed_now']).lower()}"
    )
    print(f"engine_runtime_allowed_now={str(summary['engine_runtime_allowed_now']).lower()}")
    print(f"writer_runtime_allowed_now={str(summary['writer_runtime_allowed_now']).lower()}")
    print(
        "real_result_validator_runtime_allowed_now="
        f"{str(summary['real_result_validator_runtime_allowed_now']).lower()}"
    )
    print(
        "metric_computation_allowed_now="
        f"{str(summary['metric_computation_allowed_now']).lower()}"
    )
    print(
        "result_generation_allowed_now="
        f"{str(summary['result_generation_allowed_now']).lower()}"
    )
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
    print(
        "allocation_output_allowed_now="
        f"{str(summary['allocation_output_allowed_now']).lower()}"
    )
    print(
        "trade_signal_output_allowed_now="
        f"{str(summary['trade_signal_output_allowed_now']).lower()}"
    )
    print(
        "live_recommendation_allowed_now="
        f"{str(summary['live_recommendation_allowed_now']).lower()}"
    )
    print(
        "controlled_9b_prototype_entry_allowed="
        f"{str(summary['controlled_9b_prototype_entry_allowed']).lower()}"
    )
    print(
        "default_9b_output_write_allowed="
        f"{str(summary['default_9b_output_write_allowed']).lower()}"
    )
    print(f"phase_9a8_closure_status={summary['phase_9a8_closure_status']}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
