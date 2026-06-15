"""Run recession confirmation candidate indicator diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    CandidateRecessionDiagnosticsError,
    build_candidate_recession_diagnostics,
    write_candidate_recession_diagnostics,
)

DEFAULT_WINDOWS_PATH = Path("specs/backtests/candidate_recession_diagnostic_windows.yaml")
DEFAULT_CANDIDATE_SPEC_PATH = Path("specs/backtests/recession_confirmation_candidate_indicators.yaml")
DEFAULT_GROUPS_PATH = Path("specs/common/experimental_indicator_groups.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recession_confirmation_diagnostics/"
    "candidate_recession_diagnostics.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run candidate recession confirmation diagnostics.")
    parser.add_argument("--windows", default=str(DEFAULT_WINDOWS_PATH), help="Diagnostic windows YAML path.")
    parser.add_argument("--spec", default=str(DEFAULT_CANDIDATE_SPEC_PATH), help="Candidate indicator spec path.")
    parser.add_argument("--groups", default=str(DEFAULT_GROUPS_PATH), help="Experimental indicator groups path.")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Local FRED raw cache directory.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output diagnostics JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        diagnostics = build_candidate_recession_diagnostics(
            windows_path=args.windows,
            candidate_spec_path=args.spec,
            groups_path=args.groups,
            cache_dir=args.cache_dir,
        )
        output_path = write_candidate_recession_diagnostics(args.output, diagnostics)
    except CandidateRecessionDiagnosticsError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    points_by_label = {point["label"]: point for point in diagnostics["points"]}
    aggregate = diagnostics["aggregate"]
    print(f"diagnostic_point_count={diagnostics['diagnostic_point_count']}")
    print(f"points_with_full_scores={aggregate['points_with_full_scores']}")
    print(f"points_with_missing_scores={aggregate['points_with_missing_scores']}")
    print(f"output={output_path}")
    print(f"covid_2019_status={_status(points_by_label, 'covid_false_positive_candidate')}")
    print(f"covid_2020_status={_status(points_by_label, 'covid_true_recession_candidate')}")
    print(f"gfc_status={_status(points_by_label, 'gfc_recession_confirmed')}")
    print(f"dotcom_status={_status(points_by_label, 'dotcom_recession_window')}")
    return 0


def _status(points_by_label: dict[str, dict], label: str) -> str:
    point = points_by_label.get(label)
    if not point:
        return "missing"
    return str(point["candidate_summary"]["recession_confirmation_status"])


if __name__ == "__main__":
    raise SystemExit(main())
