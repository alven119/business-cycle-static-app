from __future__ import annotations

import yaml

from business_cycle.audits.point_in_time_coverage import discover_formal_dependencies
from business_cycle.audits.scenario_as_of_inventory import summarize_scenario_as_of_inventory


def test_leaf_and_formal_output_denominators_use_same_canonical_universe() -> None:
    inventory = summarize_scenario_as_of_inventory("specs/backtests/scenarios.yaml")
    deps = discover_formal_dependencies("specs/indicator_catalog.yaml")
    catalog = yaml.safe_load(open("specs/indicator_catalog.yaml", encoding="utf-8"))
    formal_indicator_count = len(catalog["indicators"])

    canonical_count = inventory["canonical_scenario_as_of_date_count"]
    assert canonical_count == 252
    assert inventory["scenario_as_of_universe_consistent"] is True
    assert len(deps.direct_series_ids) * canonical_count == 3780
    assert formal_indicator_count * canonical_count == 3276
