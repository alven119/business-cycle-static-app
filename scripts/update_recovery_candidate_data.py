"""Update local raw cache for recovery candidate FRED series."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle import data_sources  # noqa: E402
from business_cycle.backtests import (  # noqa: E402
    CandidateIndicatorError,
    load_recovery_candidate_indicators,
    update_candidate_fred_cache,
)

DEFAULT_SPEC_PATH = Path("specs/backtests/recovery_candidate_indicators.yaml")
DEFAULT_RAW_DIR = Path("data/raw")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update FRED cache for recovery candidate indicators.")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC_PATH), help="Recovery candidate spec YAML path.")
    parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Raw cache root directory.")
    parser.add_argument("--dry-run", action="store_true", help="List required series without FRED API calls.")
    parser.add_argument("--force-refresh", action="store_true", help="Download even when cache exists.")
    parser.add_argument("--no-api", action="store_true", help="Only check local cache; do not call FRED API.")
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = update_candidate_fred_cache(
            spec_path=args.spec,
            raw_dir=args.raw_dir,
            spec_loader=load_recovery_candidate_indicators,
            summary_label="candidate recovery cache update",
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
            no_api=args.no_api,
        )
    except (CandidateIndicatorError, data_sources.FredProviderError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"required_series_count={summary['required_series_count']}")
    print(f"already_cached_series_count={summary['already_cached_series_count']}")
    print(f"downloaded_series_count={summary['downloaded_series_count']}")
    print(f"failed_series_count={summary['failed_series_count']}")
    print(f"missing_series={','.join(summary['missing_series'])}")
    print(f"cache_dir={summary['cache_dir']}")
    print(f"notes={'; '.join(summary['notes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
