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


def test_every_canonical_indicator_requirement_has_coverage_row() -> None:
    indicators = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))[
        "book_indicator_coverage"
    ]["indicators"]
    manifest = yaml.safe_load(
        Path("specs/audits/canonical_book_requirement_manifest.yaml").read_text(
            encoding="utf-8"
        )
    )["canonical_book_requirement_manifest"]["requirements"]
    required = {
        row["requirement_id"]
        for row in manifest
        if row.get("requires_indicator_coverage") is True
    }
    covered = {
        row["coverage_requirement_id"]
        for row in indicators
        if row.get("coverage_requirement_id")
    }

    assert covered == required


def test_qa4_indicator_matrix_keeps_modern_extension_separate() -> None:
    from business_cycle.audits.formal_indicator_scope_matrix import (
        build_formal_indicator_scope_matrix,
    )

    rows = build_formal_indicator_scope_matrix()
    modern_rows = [
        row for row in rows if row["book_provenance_class"] == "modern_extension"
    ]

    assert modern_rows
    assert all(
        row["scope_classification"] == "retain_as_modern_extension"
        for row in modern_rows
    )
