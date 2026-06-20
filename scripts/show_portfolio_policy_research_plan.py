"""Print a concise portfolio policy research plan summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    PortfolioPolicyResearchPlanError,
    load_portfolio_policy_research_plan,
    summarize_portfolio_policy_research_plan,
)

DEFAULT_PLAN_PATH = Path("specs/portfolio/portfolio_policy_research_plan.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show portfolio policy research plan summary.")
    parser.add_argument(
        "--plan",
        default=str(DEFAULT_PLAN_PATH),
        help="Portfolio policy research plan YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        plan = load_portfolio_policy_research_plan(args.plan)
        summary = summarize_portfolio_policy_research_plan(plan)
    except PortfolioPolicyResearchPlanError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"template_count={summary['template_count']}")
    print(f"metric_count={summary['metric_count']}")
    print(f"sensitivity_test_count={summary['sensitivity_test_count']}")
    print(f"live_allocation_allowed_now={str(summary['live_allocation_allowed_now']).lower()}")
    print(
        "trade_signal_generation_allowed_now="
        f"{str(summary['trade_signal_generation_allowed_now']).lower()}"
    )
    print(f"public_output_allowed_now={str(summary['public_output_allowed_now']).lower()}")
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
