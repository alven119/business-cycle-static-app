from __future__ import annotations

from pathlib import Path

import yaml

TRACEABILITY_PATH = Path("specs/audits/book_method_traceability.yaml")


def test_book_method_traceability_yaml_loads_and_blocks_full_alignment_claim() -> None:
    payload = yaml.safe_load(TRACEABILITY_PATH.read_text(encoding="utf-8"))
    traceability = payload["book_method_traceability"]
    rows = traceability["rows"]
    book_core = [row for row in rows if row["fidelity_class"] == "book_core"]
    missing = [row for row in book_core if row["implementation_status"] == "missing"]
    conflicting = [
        row for row in book_core if row["implementation_status"] == "conflicting"
    ]

    assert len(rows) > 22
    assert book_core
    assert missing
    assert conflicting
    assert traceability["summary"]["book_alignment_claim_allowed"] is False


def test_book_method_traceability_covers_canonical_requirement_groups() -> None:
    rows = yaml.safe_load(TRACEABILITY_PATH.read_text(encoding="utf-8"))[
        "book_method_traceability"
    ]["rows"]
    requirement_ids = {row["requirement_id"] for row in rows}

    assert "cycle_four_phase_sequence" in requirement_ids
    assert "productivity_driven_expansion" in requirement_ids
    assert "inflation_driven_expansion" in requirement_ids
    assert "recovery_initial_jobless_claims" in requirement_ids
    assert "growth_personal_saving_rate" in requirement_ids
    assert "boom_consumer_confidence" in requirement_ids
    assert "benchmark_annual_contribution_10000" in requirement_ids
    assert "boom_advanced_year_1_stock_weight_70" in requirement_ids


def test_traceability_has_no_unknown_canonical_requirement_ids() -> None:
    rows = yaml.safe_load(TRACEABILITY_PATH.read_text(encoding="utf-8"))[
        "book_method_traceability"
    ]["rows"]
    manifest = yaml.safe_load(
        Path("specs/audits/canonical_book_requirement_manifest.yaml").read_text(
            encoding="utf-8"
        )
    )["canonical_book_requirement_manifest"]["requirements"]
    manifest_ids = {row["requirement_id"] for row in manifest}
    trace_ids = {row["requirement_id"] for row in rows}

    assert trace_ids == manifest_ids
