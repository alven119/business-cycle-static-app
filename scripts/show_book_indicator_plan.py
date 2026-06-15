"""Print a concise book-aligned indicator implementation plan summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BookAlignedIndicatorImplementationPlanError,
    high_priority_indicator_count,
    load_book_aligned_indicator_implementation_plan,
    purpose_groups,
)

DEFAULT_PLAN_PATH = Path("specs/backtests/book_aligned_indicator_implementation_plan.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show book-aligned indicator implementation plan summary.")
    parser.add_argument("--plan", default=str(DEFAULT_PLAN_PATH), help="Book-aligned indicator plan YAML path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        plan = load_book_aligned_indicator_implementation_plan(args.plan)
    except BookAlignedIndicatorImplementationPlanError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    high_priority = [
        str(item["indicator_id"])
        for item in plan.candidate_indicators
        if item.get("implementation_priority") == "high"
    ]
    next_phases = [str(item["phase_id"]) for item in plan.next_phases]
    print(f"version={plan.version}")
    print(f"status={plan.status}")
    print(f"batch_count={len(plan.implementation_batches)}")
    print(f"candidate_indicator_count={len(plan.candidate_indicators)}")
    print(f"high_priority_count={high_priority_indicator_count(plan)}")
    print(f"purpose_groups={','.join(purpose_groups(plan))}")
    print(f"top_high_priority_indicators={','.join(high_priority[:8])}")
    print(f"next_phases={','.join(next_phases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
