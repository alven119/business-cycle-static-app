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

    assert len(rows) >= 20
    assert book_core
    assert missing
    assert conflicting
    assert traceability["summary"]["book_alignment_claim_allowed"] is False


def test_book_method_traceability_covers_canonical_requirement_groups() -> None:
    rows = yaml.safe_load(TRACEABILITY_PATH.read_text(encoding="utf-8"))[
        "book_method_traceability"
    ]["rows"]
    requirement_ids = {row["requirement_id"] for row in rows}

    assert "phase_order_recession_recovery_growth_boom" in requirement_ids
    assert "productivity_driven_expansion_regime" in requirement_ids
    assert "inflation_driven_expansion_regime" in requirement_ids
    assert "recovery_initial_claims" in requirement_ids
    assert "growth_saving_rate_and_income_consumption" in requirement_ids
    assert "boom_consumption_confidence_investment_inventory_defaults" in requirement_ids
    assert "portfolio_annual_contribution_rebalance" in requirement_ids
    assert "portfolio_boom_basic_and_advanced_weights" in requirement_ids


def test_modern_extensions_are_not_book_core() -> None:
    rows = yaml.safe_load(TRACEABILITY_PATH.read_text(encoding="utf-8"))[
        "book_method_traceability"
    ]["rows"]
    modern_ids = {
        row["requirement_id"]
        for row in rows
        if row["fidelity_class"] == "modern_extension"
    }

    assert "modern_extensions_not_book_core" in modern_ids

