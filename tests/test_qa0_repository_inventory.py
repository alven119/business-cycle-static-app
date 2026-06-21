from __future__ import annotations

from business_cycle.audits.repository_inventory import collect_repository_inventory


def test_repository_inventory_discovers_formal_experimental_indicators_and_series() -> None:
    summary = collect_repository_inventory()

    assert summary["discovered_formal_indicator_count"] >= 13
    assert summary["discovered_experimental_indicator_count"] >= 20
    assert summary["discovered_unique_indicator_count"] >= 38
    assert summary["discovered_direct_series_count"] > 8
    assert summary["discovered_unique_series_count"] > 8
    assert summary["discovered_phase_rule_count"] > 0
    assert summary["discovered_portfolio_artifact_count"] > 0
    assert summary["discovered_dashboard_semantic_item_count"] > 0
    assert summary["duplicate_inventory_id_count"] == 0
