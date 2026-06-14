"""Summarize a backtest timeline into diagnostics report JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import write_backtest_report  # noqa: E402

DEFAULT_BACKTEST_DIR = Path("data/backtests")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize a backtest timeline JSON.")
    parser.add_argument("--scenario-id", help="Scenario id under data/backtests.")
    parser.add_argument("--timeline", help="Path to timeline JSON.")
    parser.add_argument("--output", help="Report JSON output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.scenario_id and not args.timeline:
        parser.exit(status=1, message="error: provide --scenario-id or --timeline\n")

    timeline_path = Path(args.timeline) if args.timeline else _timeline_path(args.scenario_id)
    output_path = Path(args.output) if args.output else _default_output_path(timeline_path, args.scenario_id)
    if not timeline_path.exists():
        parser.exit(
            status=1,
            message=(
                f"error: backtest timeline does not exist: {timeline_path}. "
                "Run scripts/run_backtest.py first.\n"
            ),
        )

    try:
        output = write_backtest_report(timeline_path, output_path)
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(
        "report "
        f"scenario_id={payload['scenario_id']} "
        f"period_count={payload['period_count']} "
        f"phase_segment_count={len(payload['phase_segments'])} "
        f"transition_event_count={len(payload['transition_events'])} "
        f"first_transition_watch_as_of={payload['first_transition_watch_as_of']} "
        f"first_recession_watch_as_of={payload['first_recession_watch_as_of']} "
        f"first_recession_current_as_of={payload['first_recession_current_as_of']} "
        f"plausibility_warning_count={payload['plausibility_warning_count']} "
        f"output={output}"
    )
    for warning in payload["plausibility_warnings"][:5]:
        print(
            "plausibility_warning "
            f"kind={warning['kind']} as_of={warning['as_of']} "
            f"message_zh={warning['message_zh']}"
        )
    return 0


def _timeline_path(scenario_id: str) -> Path:
    return DEFAULT_BACKTEST_DIR / scenario_id / "timeline.json"


def _default_output_path(timeline_path: Path, scenario_id: str | None) -> Path:
    if scenario_id:
        return DEFAULT_BACKTEST_DIR / scenario_id / "report.json"
    return timeline_path.with_name("report.json")


if __name__ == "__main__":
    raise SystemExit(main())
