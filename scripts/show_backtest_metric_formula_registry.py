"""Print a concise backtest metric formula registry summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    BacktestMetricFormulaRegistryError,
    load_backtest_metric_formula_registry,
    summarize_backtest_metric_formula_registry,
)

DEFAULT_REGISTRY_PATH = Path("specs/portfolio/backtest_metric_formula_registry.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show backtest metric formula registry summary.")
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY_PATH),
        help="Backtest metric formula registry YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        registry = load_backtest_metric_formula_registry(args.registry)
        summary = summarize_backtest_metric_formula_registry(registry)
    except BacktestMetricFormulaRegistryError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"metric_count={summary['metric_count']}")
    print(f"prohibited_metric_output_count={summary['prohibited_metric_output_count']}")
    print(f"prohibited_result_field_count={summary['prohibited_result_field_count']}")
    print(
        "compute_metric_values_allowed="
        f"{str(summary['compute_metric_values_allowed']).lower()}"
    )
    print(f"execute_backtest_allowed={str(summary['execute_backtest_allowed']).lower()}")
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
    print(
        "all_metric_compute_allowed_now="
        f"{str(summary['all_metric_compute_allowed_now']).lower()}"
    )
    print(f"phase_9a2_closure_status={summary['phase_9a2_closure_status']}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
