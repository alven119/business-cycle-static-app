"""Print a concise boom-ending refinement plan summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BoomEndingRefinementPlanError,
    high_priority_refinement_count,
    load_boom_ending_refinement_plan,
)

DEFAULT_PLAN_PATH = Path("specs/backtests/boom_ending_refinement_plan.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show boom-ending refinement plan summary.")
    parser.add_argument("--plan", default=str(DEFAULT_PLAN_PATH), help="Boom-ending refinement plan YAML path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        plan = load_boom_ending_refinement_plan(args.plan)
    except BoomEndingRefinementPlanError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    reason = " ".join(str(plan.recommended_next_phase["reason_zh"]).split())
    print(f"version={plan.version}")
    print(f"status={plan.status}")
    print(f"diagnosed_issue_count={len(plan.diagnosed_issues)}")
    print(f"proposed_refinement_count={len(plan.proposed_refinements)}")
    print(f"high_priority_refinement_count={high_priority_refinement_count(plan)}")
    print(f"recommended_next_phase={plan.recommended_next_phase['phase_id']}")
    print(f"reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
