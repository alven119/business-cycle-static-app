"""Build transition attribution diagnostics for a backtest scenario."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import attribution_quality_counts, write_transition_attribution  # noqa: E402

DEFAULT_BACKTEST_DIR = Path("data/backtests")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diagnose backtest transition attribution.")
    parser.add_argument("--scenario-id", help="Scenario id under data/backtests.")
    parser.add_argument("--timeline", help="Path to timeline JSON.")
    parser.add_argument("--report", help="Path to report JSON.")
    parser.add_argument("--intermediate-dir", help="Path to scenario intermediate output directory.")
    parser.add_argument("--output", help="Transition attribution JSON output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.scenario_id and (not args.timeline or not args.report):
        parser.exit(status=1, message="error: provide --scenario-id or both --timeline and --report\n")

    timeline_path = Path(args.timeline) if args.timeline else _timeline_path(args.scenario_id)
    report_path = Path(args.report) if args.report else _report_path(args.scenario_id)
    intermediate_dir = (
        Path(args.intermediate_dir)
        if args.intermediate_dir
        else _intermediate_dir(args.scenario_id, timeline_path)
    )
    output_path = Path(args.output) if args.output else _default_output_path(args.scenario_id, timeline_path)
    missing = [str(path) for path in (timeline_path, report_path) if not path.exists()]
    if missing:
        parser.exit(
            status=1,
            message=(
                "error: missing backtest attribution input(s): "
                f"{', '.join(missing)}. Run scripts/run_backtest.py and "
                "scripts/summarize_backtest.py first.\n"
            ),
        )

    try:
        output = write_transition_attribution(
            timeline_path=timeline_path,
            report_path=report_path,
            intermediate_dir=intermediate_dir,
            output_path=output_path,
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(
        "transition_attribution "
        f"scenario_id={payload['scenario_id']} "
        f"transition_count={payload['transition_count']} "
        f"diagnostic_count={len(payload['diagnostics'])} "
        f"attribution_quality_counts={attribution_quality_counts(payload)} "
        f"output={output}"
    )
    return 0


def _timeline_path(scenario_id: str) -> Path:
    return DEFAULT_BACKTEST_DIR / scenario_id / "timeline.json"


def _report_path(scenario_id: str) -> Path:
    return DEFAULT_BACKTEST_DIR / scenario_id / "report.json"


def _intermediate_dir(scenario_id: str | None, timeline_path: Path) -> Path:
    if scenario_id:
        return DEFAULT_BACKTEST_DIR / scenario_id / "intermediate"
    return timeline_path.parent / "intermediate"


def _default_output_path(scenario_id: str | None, timeline_path: Path) -> Path:
    if scenario_id:
        return DEFAULT_BACKTEST_DIR / scenario_id / "transition_attribution.json"
    return timeline_path.with_name("transition_attribution.json")


if __name__ == "__main__":
    raise SystemExit(main())
