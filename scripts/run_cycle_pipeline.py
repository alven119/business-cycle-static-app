"""Run the local end-to-end business cycle pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.pipeline.runner import run_cycle_pipeline  # noqa: E402

DEFAULT_OUTPUT_DIR = Path("data/derived")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run local business cycle pipeline.")
    parser.add_argument("--as-of", help="Optional as-of date in YYYY-MM-DD format.")
    parser.add_argument("--previous-phase-id", help="Optional previous phase ID for resolver.")
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="Refresh catalog raw data before scoring.",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force raw data refresh when --update-data is used.",
    )
    parser.add_argument(
        "--indicator-id",
        action="append",
        help="Only process a specific indicator ID. Can be passed multiple times.",
    )
    parser.add_argument(
        "--phase-id",
        action="append",
        help="Only process a specific phase ID. Can be passed multiple times.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for derived JSON outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = run_cycle_pipeline(
        as_of=args.as_of,
        previous_phase_id=args.previous_phase_id,
        update_data=args.update_data,
        force_refresh=args.force_refresh,
        indicator_ids=args.indicator_id,
        phase_ids=args.phase_id,
        output_dir=args.output_dir,
    )
    for step in result.steps:
        print(f"step name={step['name']} exit_code={step['exit_code']} output={step['output_path']}")
    if not result.success:
        parser.exit(status=1, message=f"error: {result.message}\n")
    print(f"output indicator_scores={result.indicator_scores_path}")
    print(f"output phase_scores={result.phase_scores_path}")
    print(f"output current_phase_decision={result.current_phase_decision_path}")
    print(f"output cycle_snapshot={result.cycle_snapshot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
