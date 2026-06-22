from __future__ import annotations

from business_cycle.audits.context_source_inventory import (
    summarize_context_source_inventory,
)


def test_context_sources_are_classified_with_provenance() -> None:
    summary = summarize_context_source_inventory()

    assert summary["context_inventory_ready"] is True
    assert summary["unknown_context_source_count"] == 0
    assert summary["context_source_without_provenance_count"] == 0
    assert summary["hidden_context_consumer_count"] == 0
    assert summary["external_context_prior_count"] >= 1
