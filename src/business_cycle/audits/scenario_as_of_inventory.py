"""Canonical scenario/as-of inventory for temporal audits."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


INVENTORY_VERSION = 1


@dataclass(frozen=True)
class ScenarioAsOfEntry:
    """One canonical scenario/as-of pair."""

    scenario_id: str
    as_of: str
    source_scenario_path: str
    included_in_leaf_temporal_audit: bool = True
    included_in_formal_indicator_output_audit: bool = True
    exclusion_reason: str | None = None
    inventory_version: int = INVENTORY_VERSION

    @property
    def pair_id(self) -> str:
        return f"{self.scenario_id}|{self.as_of}"


def load_canonical_scenario_as_of_inventory(
    scenarios_path: str | Path = "specs/backtests/scenarios.yaml",
) -> list[ScenarioAsOfEntry]:
    """Build the single authoritative scenario/as-of pair universe."""

    path = Path(scenarios_path)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    entries: list[ScenarioAsOfEntry] = []
    for scenario in payload.get("scenarios", []):
        scenario_id = str(scenario["scenario_id"])
        start = pd.Timestamp(str(scenario["window_start"]))
        end = pd.Timestamp(str(scenario["window_end"]))
        for timestamp in pd.date_range(start=start, end=end, freq="ME"):
            entries.append(
                ScenarioAsOfEntry(
                    scenario_id=scenario_id,
                    as_of=timestamp.date().isoformat(),
                    source_scenario_path=str(path),
                )
            )
    return entries


def summarize_scenario_as_of_inventory(
    scenarios_path: str | Path = "specs/backtests/scenarios.yaml",
) -> dict[str, Any]:
    """Return canonical inventory counts and consistency checks."""

    entries = load_canonical_scenario_as_of_inventory(scenarios_path)
    pair_ids = [entry.pair_id for entry in entries]
    duplicate_count = len(pair_ids) - len(set(pair_ids))
    leaf_entries = [entry for entry in entries if entry.included_in_leaf_temporal_audit]
    indicator_entries = [
        entry for entry in entries if entry.included_in_formal_indicator_output_audit
    ]
    leaf_pair_ids = {entry.pair_id for entry in leaf_entries}
    indicator_pair_ids = {entry.pair_id for entry in indicator_entries}
    leaf_only = sorted(leaf_pair_ids - indicator_pair_ids)
    indicator_only = sorted(indicator_pair_ids - leaf_pair_ids)
    unexplained = len(leaf_only) + len(indicator_only)
    scenario_ids = {entry.scenario_id for entry in entries}
    return {
        "scenario_count": len(scenario_ids),
        "canonical_scenario_as_of_date_count": len(entries),
        "canonical_unique_as_of_date_count": len({entry.as_of for entry in entries}),
        "duplicate_scenario_as_of_count": duplicate_count,
        "leaf_scenario_as_of_date_count": len(leaf_entries),
        "formal_indicator_scenario_as_of_date_count": len(indicator_entries),
        "leaf_only_as_of_count": len(leaf_only),
        "indicator_only_as_of_count": len(indicator_only),
        "unexplained_as_of_divergence_count": unexplained,
        "scenario_as_of_universe_consistent": duplicate_count == 0 and unexplained == 0,
        "inventory_version": INVENTORY_VERSION,
        "leaf_only_pair_ids": leaf_only,
        "indicator_only_pair_ids": indicator_only,
    }
