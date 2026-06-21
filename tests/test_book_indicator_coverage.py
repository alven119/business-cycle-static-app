from __future__ import annotations

from pathlib import Path

import yaml

COVERAGE_PATH = Path("specs/audits/book_indicator_coverage.yaml")


def test_missing_book_core_indicator_blocks_alignment_claim() -> None:
    coverage = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))[
        "book_indicator_coverage"
    ]
    indicators = coverage["indicators"]
    missing = [
        item for item in indicators if item["book_alignment_status"] == "missing"
    ]

    assert missing
    assert coverage["summary"]["book_alignment_claim_allowed"] is False


def test_modern_extension_is_not_marked_book_core() -> None:
    indicators = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))[
        "book_indicator_coverage"
    ]["indicators"]
    yield_curve = next(item for item in indicators if item["indicator_id"] == "yield_curve_spread")

    assert yield_curve["provenance_class"] == "modern_extension"
    assert yield_curve["substitute_is_equivalent"] is False

