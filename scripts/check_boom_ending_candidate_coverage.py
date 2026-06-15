"""Check local coverage for boom-ending candidate FRED series."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    CandidateIndicatorError,
    check_boom_ending_candidate_coverage,
)

DEFAULT_SPEC_PATH = Path("specs/backtests/boom_ending_candidate_indicators.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check local raw cache coverage for boom-ending candidates.")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC_PATH), help="Boom-ending candidate spec YAML path.")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Local FRED raw CSV cache directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = check_boom_ending_candidate_coverage(spec_path=args.spec, cache_dir=args.cache_dir)
    except CandidateIndicatorError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"candidate_indicator_count={summary['candidate_indicator_count']}")
    print(f"required_series_count={summary['required_series_count']}")
    print(f"available_series_count={summary['available_series_count']}")
    print(f"cached_series={','.join(summary['cached_series'])}")
    print(f"missing_series={','.join(summary['missing_series'])}")
    print(f"derived_series={','.join(summary['derived_series'])}")
    print(f"notes={'; '.join(summary['notes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
