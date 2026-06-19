"""Run recovery candidate indicator diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    RecoveryDiagnosticsError,
    build_recovery_diagnostics,
    write_recovery_diagnostics,
)

DEFAULT_WINDOWS_PATH = Path("specs/backtests/recovery_diagnostic_windows.yaml")
DEFAULT_CANDIDATE_SPEC_PATH = Path("specs/backtests/recovery_candidate_indicators.yaml")
DEFAULT_GROUPS_PATH = Path("specs/common/experimental_indicator_groups.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_diagnostics/recovery_diagnostics.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run recovery candidate diagnostics.")
    parser.add_argument("--windows", default=str(DEFAULT_WINDOWS_PATH), help="Diagnostic windows YAML path.")
    parser.add_argument("--spec", default=str(DEFAULT_CANDIDATE_SPEC_PATH), help="Recovery candidate spec path.")
    parser.add_argument("--groups", default=str(DEFAULT_GROUPS_PATH), help="Experimental indicator groups path.")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Local FRED raw cache directory.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output diagnostics JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        diagnostics = build_recovery_diagnostics(
            windows_path=args.windows,
            spec_path=args.spec,
            groups_path=args.groups,
            cache_dir=args.cache_dir,
        )
        output_path = write_recovery_diagnostics(args.output, diagnostics)
    except RecoveryDiagnosticsError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    summary = diagnostics["summary"]
    print(f"diagnostic_point_count={diagnostics['diagnostic_point_count']}")
    print(f"points_with_full_scores={diagnostics['points_with_full_scores']}")
    print(f"points_with_missing_scores={diagnostics['points_with_missing_scores']}")
    print(f"match_count={summary['match_count']}")
    print(f"mismatch_count={summary['mismatch_count']}")
    print(f"strong_count={summary['strong_count']}")
    print(f"watch_count={summary['watch_count']}")
    print(f"weak_count={summary['weak_count']}")
    print(f"none_count={summary['none_count']}")
    print(f"policy_only_warning_count={summary['policy_only_warning_count']}")
    print(f"unexpected_strong_points={','.join(summary['unexpected_strong_points'])}")
    print(f"missed_recovery_watch_points={','.join(summary['missed_recovery_watch_points'])}")
    print(f"indicators_requiring_refinement={','.join(summary['indicators_requiring_refinement'])}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
