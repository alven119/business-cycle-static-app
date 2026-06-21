"""Print a concise real backtest prototype readiness gate summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    RealBacktestPrototypeReadinessGateError,
    load_real_backtest_prototype_readiness_gate,
    summarize_real_backtest_prototype_readiness_gate,
)

DEFAULT_GATE_PATH = Path("specs/portfolio/real_backtest_prototype_readiness_gate.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show real backtest prototype readiness gate summary."
    )
    parser.add_argument(
        "--gate",
        default=str(DEFAULT_GATE_PATH),
        help="Real backtest prototype readiness gate YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        gate = load_real_backtest_prototype_readiness_gate(args.gate)
        summary = summarize_real_backtest_prototype_readiness_gate(gate)
    except RealBacktestPrototypeReadinessGateError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"required_contract_count={summary['required_contract_count']}")
    print(f"active_blocker_count={summary['active_blocker_count']}")
    print(f"allowed_future_phase_count={summary['allowed_future_phase_count']}")
    print(f"readiness_conclusion_status={summary['readiness_conclusion_status']}")
    print(f"research_only_required={str(summary['research_only_required']).lower()}")
    print(
        "structural_dry_run_only_required="
        f"{str(summary['structural_dry_run_only_required']).lower()}"
    )
    print(
        "real_backtest_execution_allowed="
        f"{str(summary['real_backtest_execution_allowed']).lower()}"
    )
    print(f"performance_metrics_allowed={str(summary['performance_metrics_allowed']).lower()}")
    print(
        "backtest_result_output_allowed="
        f"{str(summary['backtest_result_output_allowed']).lower()}"
    )
    print(f"allocation_output_allowed={str(summary['allocation_output_allowed']).lower()}")
    print(f"trade_signal_output_allowed={str(summary['trade_signal_output_allowed']).lower()}")
    print(
        "data_backtests_output_allowed="
        f"{str(summary['data_backtests_output_allowed']).lower()}"
    )
    print(f"public_output_allowed={str(summary['public_output_allowed']).lower()}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
