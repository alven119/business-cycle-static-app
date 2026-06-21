#!/usr/bin/env python
"""Show QA0 repository inventory summary."""

from __future__ import annotations

from business_cycle.audits.repository_inventory import collect_repository_inventory


def main() -> int:
    summary = collect_repository_inventory()
    keys = (
        "discovered_formal_indicator_count",
        "discovered_experimental_indicator_count",
        "discovered_unique_indicator_count",
        "discovered_direct_series_count",
        "discovered_derived_series_count",
        "discovered_unique_series_count",
        "discovered_phase_rule_count",
        "discovered_portfolio_artifact_count",
        "discovered_dashboard_semantic_item_count",
        "duplicate_inventory_id_count",
        "duplicate_series_alias_count",
    )
    for key in keys:
        print(f"{key}={summary[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
