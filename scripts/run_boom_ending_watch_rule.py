"""Run experimental boom-ending watch rule on refined diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BoomEndingWatchRuleError,
    build_boom_ending_watch_rule_report,
    load_boom_ending_watch_rule,
    write_boom_ending_watch_rule_report,
)

DEFAULT_REFINEMENT_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_refinement/"
    "boom_ending_refinement_experiment.json"
)
DEFAULT_RULE_PATH = Path("specs/backtests/boom_ending_watch_rule.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_watch_rule/"
    "boom_ending_watch_rule_report.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run experimental boom-ending watch rule.")
    parser.add_argument("--refinement", default=str(DEFAULT_REFINEMENT_PATH), help="Refinement experiment JSON path.")
    parser.add_argument("--rule", default=str(DEFAULT_RULE_PATH), help="Boom ending watch rule YAML path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output report JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        rule = load_boom_ending_watch_rule(args.rule)
        report = build_boom_ending_watch_rule_report(args.refinement, rule)
        output_path = write_boom_ending_watch_rule_report(args.output, report)
    except BoomEndingWatchRuleError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    summary = report["summary"]
    print(f"point_count={report['point_count']}")
    print(f"match_count={summary['match_count']}")
    print(f"mismatch_count={summary['mismatch_count']}")
    print(f"strong_late_cycle_warning_count={summary['strong_late_cycle_warning_count']}")
    print(f"watch_count={summary['watch_count']}")
    print(f"weak_count={summary['weak_count']}")
    print(f"none_count={summary['none_count']}")
    print(f"unexpected_strong_points={','.join(summary['unexpected_strong_points'])}")
    print(f"missed_watch_points={','.join(summary['missed_watch_points'])}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
