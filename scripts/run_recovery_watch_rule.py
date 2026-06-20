"""Run experimental recovery watch rule on refined diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    RecoveryWatchRuleError,
    build_recovery_watch_rule_report,
    load_recovery_watch_rule,
    write_recovery_watch_rule_report,
)

DEFAULT_REFINEMENT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_refinement/"
    "recovery_refinement_experiment.json"
)
DEFAULT_RULE_PATH = Path("specs/backtests/recovery_watch_rule.yaml")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_watch_rule/"
    "recovery_watch_rule_report.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run experimental recovery watch rule.")
    parser.add_argument("--refinement", default=str(DEFAULT_REFINEMENT_PATH), help="Refinement experiment JSON path.")
    parser.add_argument("--rule", default=str(DEFAULT_RULE_PATH), help="Recovery watch rule YAML path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output report JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        rule = load_recovery_watch_rule(args.rule)
        report = build_recovery_watch_rule_report(args.refinement, rule)
        output_path = write_recovery_watch_rule_report(args.output, report)
    except RecoveryWatchRuleError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    summary = report["summary"]
    print(f"point_count={report['point_count']}")
    print(f"match_count={summary['match_count']}")
    print(f"mismatch_count={summary['mismatch_count']}")
    print(f"strong_recovery_watch_count={summary['strong_recovery_watch_count']}")
    print(f"recovery_watch_count={summary['recovery_watch_count']}")
    print(f"weak_count={summary['weak_count']}")
    print(f"none_count={summary['none_count']}")
    print(f"policy_only_blocked_count={summary['policy_only_blocked_count']}")
    print(f"context_gate_blocked_count={summary['context_gate_blocked_count']}")
    print(f"unexpected_strong_points={','.join(summary['unexpected_strong_points'])}")
    print(f"missed_recovery_watch_points={','.join(summary['missed_recovery_watch_points'])}")
    print(f"non_recession_watch_points={','.join(summary['non_recession_watch_points'])}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
