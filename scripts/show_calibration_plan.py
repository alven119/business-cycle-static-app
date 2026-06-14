"""Print a concise calibration plan summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import CalibrationPlanError, load_calibration_plan  # noqa: E402

DEFAULT_PLAN_PATH = Path("specs/backtests/calibration_plan.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show model calibration plan summary.")
    parser.add_argument(
        "--plan",
        default=str(DEFAULT_PLAN_PATH),
        help="Calibration plan YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        plan = load_calibration_plan(args.plan)
    except CalibrationPlanError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={plan.version}")
    print(f"status={plan.status}")
    print(f"diagnosed_issue_count={len(plan.diagnosed_issues)}")
    print(f"candidate_controls={','.join(sorted(plan.candidate_model_controls))}")
    print(f"in_sample_scenarios={','.join(plan.calibration_scenarios['in_sample'])}")
    print(f"out_of_sample_scenarios={','.join(plan.calibration_scenarios['out_of_sample'])}")
    print(f"acceptance_criteria_count={len(plan.acceptance_criteria)}")
    print(
        "next_phases="
        + ",".join(f"{phase['phase_id']}:{phase['title']}" for phase in plan.next_phases)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
