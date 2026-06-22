from __future__ import annotations

from business_cycle.audits.scenario_as_of_inventory import (
    load_canonical_scenario_as_of_inventory,
    summarize_scenario_as_of_inventory,
)


def test_canonical_scenario_as_of_inventory_preserves_scenario_pairs() -> None:
    entries = load_canonical_scenario_as_of_inventory("specs/backtests/scenarios.yaml")
    summary = summarize_scenario_as_of_inventory("specs/backtests/scenarios.yaml")

    assert len(entries) == 252
    assert summary["canonical_scenario_as_of_date_count"] == 252
    assert summary["canonical_unique_as_of_date_count"] == 228
    assert summary["duplicate_scenario_as_of_count"] == 0
    assert summary["leaf_scenario_as_of_date_count"] == summary[
        "formal_indicator_scenario_as_of_date_count"
    ]
    assert summary["unexplained_as_of_divergence_count"] == 0
    assert summary["scenario_as_of_universe_consistent"] is True
