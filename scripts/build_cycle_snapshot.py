"""Build an end-to-end cycle snapshot JSON."""

from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.phases.state_machine import load_current_phase_decision_json
from business_cycle.pipeline.snapshot import (
    build_cycle_snapshot,
    load_indicator_score_summary_json,
    load_phase_score_summary_json,
    write_cycle_snapshot_json,
)

DEFAULT_INDICATOR_SCORES_PATH = Path("data/derived/indicator_scores.json")
DEFAULT_PHASE_SCORES_PATH = Path("data/derived/phase_scores.json")
DEFAULT_CURRENT_PHASE_DECISION_PATH = Path("data/derived/current_phase_decision.json")
DEFAULT_OUTPUT_PATH = Path("data/derived/cycle_snapshot.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build cycle snapshot JSON.")
    parser.add_argument(
        "--indicator-scores-path",
        default=str(DEFAULT_INDICATOR_SCORES_PATH),
        help="Path to Phase 2F indicator_scores.json.",
    )
    parser.add_argument(
        "--phase-scores-path",
        default=str(DEFAULT_PHASE_SCORES_PATH),
        help="Path to Phase 3C phase_scores.json.",
    )
    parser.add_argument(
        "--current-phase-decision-path",
        default=str(DEFAULT_CURRENT_PHASE_DECISION_PATH),
        help="Path to Phase 4A current_phase_decision.json.",
    )
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Cycle snapshot JSON output path.",
    )
    parser.add_argument("--as-of", help="Optional snapshot as-of date in YYYY-MM-DD format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        indicator_summary = load_indicator_score_summary_json(args.indicator_scores_path)
        phase_summary = load_phase_score_summary_json(args.phase_scores_path)
        decision = load_current_phase_decision_json(args.current_phase_decision_path)
    except FileNotFoundError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    snapshot = build_cycle_snapshot(
        indicator_scores_summary=indicator_summary,
        phase_scores_summary=phase_summary,
        current_phase_decision=decision,
        as_of=args.as_of,
    )
    output_path = write_cycle_snapshot_json(snapshot, args.output_path)
    print(
        "snapshot "
        f"current_phase_id={snapshot.summary['current_phase_id']} "
        f"decision_status={snapshot.summary['decision_status']} "
        f"confidence={snapshot.summary['decision_confidence']} "
        f"output={output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
