"""Check local coverage for recession confirmation candidate FRED series."""

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
    load_recession_confirmation_candidate_indicators,
)

DEFAULT_SPEC_PATH = Path("specs/backtests/recession_confirmation_candidate_indicators.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check local raw cache coverage for candidate indicators.")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC_PATH), help="Candidate indicator spec YAML path.")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Local FRED raw CSV cache directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        spec = load_recession_confirmation_candidate_indicators(args.spec)
    except CandidateIndicatorError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    cache_dir = Path(args.cache_dir)
    required_series: set[str] = set()
    missing_series: list[str] = []
    available_series: list[str] = []
    derived_series: list[str] = []
    for indicator in spec.indicators:
        series_ids = [str(item).upper() for item in indicator.get("candidate_fred_series", [])]
        required_series.update(series_ids)
        if indicator.get("derived_formula"):
            derived_series.append(str(indicator["indicator_id"]))
        for series_id in series_ids:
            if (cache_dir / f"{series_id}.csv").exists():
                available_series.append(series_id)
            else:
                missing_series.append(series_id)

    available_unique = sorted(set(available_series))
    missing_unique = sorted(set(missing_series))
    print(f"candidate_indicator_count={len(spec.indicators)}")
    print(f"required_series_count={len(required_series)}")
    print(f"available_series_count={len(available_unique)}")
    print(f"missing_series={','.join(missing_unique)}")
    print(f"derived_series={','.join(sorted(derived_series))}")
    print("notes=local cache check only; no FRED API calls were made")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
