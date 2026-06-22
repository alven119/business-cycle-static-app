from __future__ import annotations

from pathlib import Path

import yaml

from business_cycle.audits.book_faithful_scope import (
    build_book_faithful_scope_items,
    summarize_book_faithful_formal_model_scope,
)


def test_every_book_core_requirement_has_exactly_one_scope_item() -> None:
    manifest = yaml.safe_load(
        Path("specs/audits/canonical_book_requirement_manifest.yaml").read_text(
            encoding="utf-8"
        )
    )["canonical_book_requirement_manifest"]["requirements"]
    book_core_ids = {
        row["requirement_id"]
        for row in manifest
        if row["book_fidelity_class"] == "book_core"
    }
    items = build_book_faithful_scope_items()
    mapped = [
        item["book_requirement_id"]
        for item in items
        if item["book_fidelity_class"] == "book_core"
    ]

    assert set(mapped) == book_core_ids
    assert len(mapped) == len(set(mapped))


def test_scope_counts_preserve_missing_and_conflicting_items() -> None:
    summary = summarize_book_faithful_formal_model_scope()

    assert summary["book_faithful_scope_contract_ready"] is True
    assert summary["formal_scope_item_count"] == 98
    assert summary["book_core_scope_item_count"] == 77
    assert summary["missing_scope_item_count"] > 0
    assert summary["conflicting_scope_item_count"] > 0
    assert summary["book_faithful_scope_complete"] is False
    assert summary["book_alignment_claim_allowed"] is False


def test_missing_item_cannot_be_marked_ready() -> None:
    items = build_book_faithful_scope_items()
    growth_adp = next(
        item for item in items if item["book_requirement_id"] == "growth_adp_employment"
    )

    assert growth_adp["current_implementation_status"] == "missing"
    assert growth_adp["decision_rule_ready"] is False

