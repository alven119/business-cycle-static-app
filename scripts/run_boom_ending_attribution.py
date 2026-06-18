"""Run attribution for boom-ending candidate diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BoomEndingAttributionError,
    build_boom_ending_attribution_from_file,
    write_boom_ending_attribution,
)

DEFAULT_DIAGNOSTICS_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_diagnostics/"
    "boom_ending_diagnostics.json"
)
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_diagnostics/"
    "boom_ending_attribution.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run boom-ending diagnostics attribution.")
    parser.add_argument("--diagnostics", default=str(DEFAULT_DIAGNOSTICS_PATH), help="Boom-ending diagnostics JSON path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output attribution JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        attribution = build_boom_ending_attribution_from_file(args.diagnostics)
        output_path = write_boom_ending_attribution(args.output, attribution)
    except BoomEndingAttributionError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    gfc = attribution["comparisons"].get("gfc_progression", {})
    print(f"point_count={attribution['point_count']}")
    print(f"refinement_candidate_count={len(attribution['refinement_candidates'])}")
    print(f"gfc_progression_status={','.join(gfc.get('status_trend', []))}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
