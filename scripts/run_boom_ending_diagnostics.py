"""Run boom-ending candidate indicator diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BoomEndingDiagnosticsError,
    build_boom_ending_diagnostics,
    write_boom_ending_diagnostics,
)

DEFAULT_WINDOWS_PATH = Path("specs/backtests/boom_ending_diagnostic_windows.yaml")
DEFAULT_CANDIDATE_SPEC_PATH = Path("specs/backtests/boom_ending_candidate_indicators.yaml")
DEFAULT_GROUPS_PATH = Path("specs/common/experimental_indicator_groups.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/boom_ending_diagnostics/"
    "boom_ending_diagnostics.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run boom-ending candidate diagnostics.")
    parser.add_argument("--windows", default=str(DEFAULT_WINDOWS_PATH), help="Diagnostic windows YAML path.")
    parser.add_argument("--spec", default=str(DEFAULT_CANDIDATE_SPEC_PATH), help="Boom-ending candidate spec path.")
    parser.add_argument("--groups", default=str(DEFAULT_GROUPS_PATH), help="Experimental indicator groups path.")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Local FRED raw cache directory.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output diagnostics JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        diagnostics = build_boom_ending_diagnostics(
            windows_path=args.windows,
            candidate_spec_path=args.spec,
            groups_path=args.groups,
            cache_dir=args.cache_dir,
        )
        output_path = write_boom_ending_diagnostics(args.output, diagnostics)
    except BoomEndingDiagnosticsError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    points_by_label = {point["label"]: point for point in diagnostics["points"]}
    aggregate = diagnostics["aggregate"]
    print(f"diagnostic_point_count={diagnostics['diagnostic_point_count']}")
    print(f"points_with_full_scores={aggregate['points_with_full_scores']}")
    print(f"points_with_missing_scores={aggregate['points_with_missing_scores']}")
    print(f"output={output_path}")
    print(f"dotcom_peak_status={_status(points_by_label, 'dotcom_market_peak_area')}")
    print(f"gfc_2006_status={_status(points_by_label, 'gfc_yield_curve_warning')}")
    print(f"gfc_2007_status={_status(points_by_label, 'gfc_recession_window_start')}")
    print(f"covid_2019_status={_status(points_by_label, 'covid_2019_false_recession_context')}")
    print(f"late_cycle_2018_status={_status(points_by_label, 'late_cycle_2018_warning')}")
    return 0


def _status(points_by_label: dict[str, dict], label: str) -> str:
    point = points_by_label.get(label)
    if not point:
        return "missing"
    return str(point["candidate_summary"]["boom_ending_status"])


if __name__ == "__main__":
    raise SystemExit(main())
