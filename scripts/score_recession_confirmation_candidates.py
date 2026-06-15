"""Score experimental recession confirmation candidate indicators from local cache."""

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
    score_candidate_indicators,
    write_candidate_indicator_scores,
)

DEFAULT_SPEC_PATH = Path("specs/backtests/recession_confirmation_candidate_indicators.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")
DEFAULT_OUTPUT_ROOT = Path("data/backtests/candidate_indicators/recession_confirmation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score experimental recession confirmation candidate indicators from local raw cache."
    )
    parser.add_argument("--as-of", required=True, help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC_PATH), help="Candidate indicator spec YAML path.")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Local FRED raw CSV cache directory.")
    parser.add_argument("--output", help="Output JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = Path(args.output) if args.output else DEFAULT_OUTPUT_ROOT / args.as_of / "candidate_indicator_scores.json"
    try:
        scores = score_candidate_indicators(
            as_of=args.as_of,
            cache_dir=args.cache_dir,
            spec_path=args.spec,
        )
        output_path = write_candidate_indicator_scores(output, scores)
    except CandidateIndicatorError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"as_of={scores['as_of']}")
    print(f"total_candidates={scores['total_candidates']}")
    print(f"scored_candidates={scores['scored_candidates']}")
    print(f"failed_candidates={scores['failed_candidates']}")
    print(f"output={output_path}")
    if scores["warnings"]:
        print(f"warnings={len(scores['warnings'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
