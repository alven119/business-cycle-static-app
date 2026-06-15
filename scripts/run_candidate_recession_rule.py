"""Run experimental recession confirmation rule on candidate diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    CandidateRecessionRuleError,
    build_candidate_recession_rule_report,
    load_candidate_recession_confirmation_rule,
    write_candidate_recession_rule_report,
)

DEFAULT_DIAGNOSTICS_PATH = Path(
    "data/backtests/candidate_indicators/recession_confirmation_diagnostics/"
    "candidate_recession_diagnostics.json"
)
DEFAULT_RULE_PATH = Path("specs/backtests/candidate_recession_confirmation_rule.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recession_confirmation_rule/"
    "candidate_recession_rule_report.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run experimental candidate recession confirmation rule.")
    parser.add_argument("--diagnostics", default=str(DEFAULT_DIAGNOSTICS_PATH), help="Candidate diagnostics JSON path.")
    parser.add_argument("--rule", default=str(DEFAULT_RULE_PATH), help="Candidate recession rule YAML path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output report JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        rule = load_candidate_recession_confirmation_rule(args.rule)
        report = build_candidate_recession_rule_report(args.diagnostics, rule)
        output_path = write_candidate_recession_rule_report(args.output, report)
    except CandidateRecessionRuleError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    summary = report["summary"]
    print(f"point_count={report['point_count']}")
    print(f"match_count={summary['match_count']}")
    print(f"mismatch_count={summary['mismatch_count']}")
    print(f"confirmed_count={summary['confirmed_count']}")
    print(f"watch_count={summary['watch_count']}")
    print(f"weak_count={summary['weak_count']}")
    print(f"none_count={summary['none_count']}")
    print(f"false_confirmed_points={','.join(summary['false_confirmed_points'])}")
    print(f"missed_confirmed_points={','.join(summary['missed_confirmed_points'])}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
