"""Run attribution for recovery candidate diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    RecoveryAttributionError,
    build_recovery_attribution_from_file,
    write_recovery_attribution,
)

DEFAULT_DIAGNOSTICS_PATH = Path(
    "data/backtests/candidate_indicators/recovery_diagnostics/recovery_diagnostics.json"
)
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_diagnostics/recovery_attribution.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run recovery diagnostics attribution.")
    parser.add_argument("--diagnostics", default=str(DEFAULT_DIAGNOSTICS_PATH), help="Recovery diagnostics JSON path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output attribution JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        attribution = build_recovery_attribution_from_file(args.diagnostics)
        output_path = write_recovery_attribution(args.output, attribution)
    except RecoveryAttributionError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    summary_points = {str(item) for item in attribution["comparisons"]["false_positive_review"].get("points", [])}
    unexpected = [
        f"{point['scenario_id']}:{point['as_of']}:{point['label']}"
        for point in attribution["points"]
        if point["recovery_status"] == "strong" and point["expected_status"] in {"weak_or_none", "weak_or_watch"}
    ]
    missed = [
        f"{point['scenario_id']}:{point['as_of']}:{point['label']}"
        for point in attribution["points"]
        if point["expected_status"] == "watch_or_strong" and point["recovery_status"] in {"weak", "none"}
    ]
    print(f"point_count={attribution['point_count']}")
    print(f"mismatch_count={attribution['mismatch_count']}")
    print(f"refinement_candidate_count={len(attribution['refinement_candidates'])}")
    print(f"unexpected_strong_points={','.join(unexpected)}")
    print(f"missed_recovery_watch_points={','.join(missed)}")
    print(f"false_positive_review_points={','.join(sorted(summary_points))}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
