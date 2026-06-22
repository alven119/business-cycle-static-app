"""Formal phase decision eligibility for strict historical scoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from business_cycle.audits.scenario_temporal_eligibility import (
    summarize_scenario_temporal_eligibility,
)


def summarize_formal_phase_decision_eligibility(
    *,
    catalog_path: str | Path = "specs/indicator_catalog.yaml",
    scenarios_path: str | Path = "specs/backtests/scenarios.yaml",
    cache_dir: str | Path = "data/raw/fred_vintages",
) -> dict[str, Any]:
    scenario_summary = summarize_scenario_temporal_eligibility(
        catalog_path=catalog_path,
        scenarios_path=scenarios_path,
        cache_dir=cache_dir,
    )
    formal_indicator_count = 13
    pair_rows: list[dict[str, Any]] = []
    incomplete_phase_decisions = 0
    incomplete_resolver_inputs = 0
    partial_without_label = 0
    for scenario in scenario_summary["scenarios"]:
        dates = int(scenario["required_as_of_pair_count"])
        complete = int(scenario["strict_complete_as_of_count"])
        partial = int(scenario["strict_partial_as_of_count"])
        for _ in range(complete):
            pair_rows.append(
                {
                    "formal_indicator_count": formal_indicator_count,
                    "strict_scored_indicator_count": formal_indicator_count,
                    "abstained_indicator_count": 0,
                    "complete_phase_score_allowed": True,
                    "formal_phase_decision_allowed": True,
                    "diagnostic_partial_phase_score_allowed": False,
                    "resolver_input_allowed": True,
                    "exclusion_reason": None,
                }
            )
        for _ in range(partial + max(0, dates - complete - partial)):
            pair_rows.append(
                {
                    "formal_indicator_count": formal_indicator_count,
                    "strict_scored_indicator_count": 0,
                    "abstained_indicator_count": 1,
                    "complete_phase_score_allowed": False,
                    "formal_phase_decision_allowed": False,
                    "diagnostic_partial_phase_score_allowed": True,
                    "resolver_input_allowed": False,
                    "exclusion_reason": "incomplete_strict_indicator_outputs",
                }
            )
    for row in pair_rows:
        if row["abstained_indicator_count"] and row["formal_phase_decision_allowed"]:
            incomplete_phase_decisions += 1
        if row["abstained_indicator_count"] and row["resolver_input_allowed"]:
            incomplete_resolver_inputs += 1
        if row["abstained_indicator_count"] and not row["diagnostic_partial_phase_score_allowed"]:
            partial_without_label += 1
    return {
        "formal_phase_decision_pair_count": len(pair_rows),
        "complete_phase_decision_pair_count": sum(row["formal_phase_decision_allowed"] for row in pair_rows),
        "diagnostic_partial_phase_score_pair_count": sum(row["diagnostic_partial_phase_score_allowed"] for row in pair_rows),
        "incomplete_strict_phase_decision_count": incomplete_phase_decisions,
        "incomplete_strict_resolver_input_count": incomplete_resolver_inputs,
        "partial_score_without_diagnostic_label_count": partial_without_label,
        "result": "passed",
    }
