"""Print a concise book indicator gap analysis summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BookIndicatorGapAnalysisError,
    high_priority_book_gap_count,
    load_book_indicator_gap_analysis,
    sensitivity_issues,
)

DEFAULT_SPEC_PATH = Path("specs/backtests/book_indicator_gap_analysis.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show book-aligned indicator gap analysis summary.")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC_PATH), help="Book indicator gap analysis YAML path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        analysis = load_book_indicator_gap_analysis(args.spec)
    except BookIndicatorGapAnalysisError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    top_recommendations = [
        str(item["recommendation_id"])
        for item in analysis.priority_recommendations
        if item.get("priority") == "high"
    ]
    print(f"version={analysis.version}")
    print(f"status={analysis.status}")
    print(f"group_count={len(analysis.book_aligned_indicator_groups)}")
    print(f"gap_count={len(analysis.gap_items)}")
    print(f"high_priority_count={high_priority_book_gap_count(analysis)}")
    print(f"sensitivity_issue_count={len(sensitivity_issues(analysis))}")
    print(f"top_priority_recommendations={','.join(top_recommendations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
