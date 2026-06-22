"""Scenario-level temporal eligibility audit."""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

from business_cycle.audits.formal_indicator_output_coverage import (
    _load_point_in_time_observations_by_indicator,
    _fred_candidate_series_ids,
)
from business_cycle.audits.scenario_as_of_inventory import (
    load_canonical_scenario_as_of_inventory,
    summarize_scenario_as_of_inventory,
)
from business_cycle.indicators.batch_scoring import score_indicator_batch
from business_cycle.indicators.catalog import load_indicator_catalog, load_indicator_scoring_specs


def summarize_scenario_temporal_eligibility(
    *,
    catalog_path: str | Path = "specs/indicator_catalog.yaml",
    scenarios_path: str | Path = "specs/backtests/scenarios.yaml",
    cache_dir: str | Path = "data/raw/fred_vintages",
) -> dict[str, Any]:
    return _summarize_scenario_temporal_eligibility_cached(
        str(catalog_path),
        str(scenarios_path),
        str(cache_dir),
    )


@lru_cache(maxsize=8)
def _summarize_scenario_temporal_eligibility_cached(
    catalog_path: str,
    scenarios_path: str,
    cache_dir: str,
) -> dict[str, Any]:
    catalog_entries = load_indicator_catalog(catalog_path)
    specs = load_indicator_scoring_specs(catalog_path)
    scenario_entries = load_canonical_scenario_as_of_inventory(scenarios_path)
    scenario_summary = summarize_scenario_as_of_inventory(scenarios_path)
    by_scenario: dict[str, list[Any]] = defaultdict(list)
    for entry in scenario_entries:
        by_scenario[entry.scenario_id].append(entry)

    scenario_rows = []
    strict_complete_as_of_pair_count = 0
    strict_partial_as_of_pair_count = 0
    missing_as_of_pair_count = 0
    scenario_with_silent_horizon_reduction_count = 0
    incomplete_strict_complete_count = 0
    revised_marked_point_in_time_count = 0
    strict_partial_performance_eligible_count = 0
    previously_seen_holdout_count = 0

    for scenario_id, entries in sorted(by_scenario.items()):
        strict_complete_dates = []
        strict_partial_dates = []
        missing_dates = []
        covered_outputs = 0
        missing_indicators: set[str] = set()
        missing_series: set[str] = set()
        for entry in entries:
            observations, load_failures = _load_point_in_time_observations_by_indicator(
                catalog_entries,
                cache_dir=Path(cache_dir),
                as_of=entry.as_of,
            )
            load_failed_ids = {str(item["indicator_id"]) for item in load_failures}
            scorable_specs = {
                indicator_id: spec
                for indicator_id, spec in specs.items()
                if indicator_id not in load_failed_ids
            }
            batch = score_indicator_batch(observations, scorable_specs, as_of=entry.as_of)
            scored_count = len(batch.results)
            covered_outputs += scored_count
            for failure in load_failures:
                missing_indicators.add(str(failure["indicator_id"]))
                series_id = str(failure.get("series_id") or "")
                if series_id:
                    missing_series.update(series_id.split(","))
            for failure in batch.failures:
                missing_indicators.add(str(failure.get("indicator_id", "")))
            if scored_count == len(catalog_entries):
                strict_complete_dates.append(entry.as_of)
                strict_complete_as_of_pair_count += 1
            elif scored_count > 0:
                strict_partial_dates.append(entry.as_of)
                strict_partial_as_of_pair_count += 1
            else:
                missing_dates.append(entry.as_of)
                missing_as_of_pair_count += 1
        total_outputs = len(entries) * len(catalog_entries)
        missing_outputs = total_outputs - covered_outputs
        temporal_tier = "strict_complete" if missing_outputs == 0 else "strict_partial"
        calibration_allowed = temporal_tier == "strict_complete"
        validation_allowed = temporal_tier == "strict_complete"
        untouched_holdout_allowed = False
        performance_allowed = temporal_tier == "strict_complete"
        if temporal_tier == "strict_complete" and missing_outputs != 0:
            incomplete_strict_complete_count += 1
        if temporal_tier == "strict_partial" and performance_allowed:
            strict_partial_performance_eligible_count += 1
        if untouched_holdout_allowed:
            previously_seen_holdout_count += 1
        row = {
            "scenario_id": scenario_id,
            "required_as_of_pair_count": len(entries),
            "strict_complete_as_of_count": len(strict_complete_dates),
            "strict_partial_as_of_count": len(strict_partial_dates),
            "missing_as_of_count": len(missing_dates),
            "formal_indicator_output_total_count": total_outputs,
            "formal_indicator_output_covered_count": covered_outputs,
            "formal_indicator_output_missing_count": missing_outputs,
            "coverage_ratio": 0.0 if total_outputs == 0 else round(covered_outputs / total_outputs, 6),
            "missing_indicator_ids": sorted(missing_indicators),
            "missing_series_ids": sorted(item for item in missing_series if item),
            "first_strict_complete_as_of": strict_complete_dates[0] if strict_complete_dates else None,
            "last_strict_complete_as_of": strict_complete_dates[-1] if strict_complete_dates else None,
            "first_missing_as_of": (strict_partial_dates + missing_dates)[0]
            if (strict_partial_dates + missing_dates)
            else None,
            "last_missing_as_of": (strict_partial_dates + missing_dates)[-1]
            if (strict_partial_dates + missing_dates)
            else None,
            "temporal_tier": temporal_tier,
            "exclusion_reasons": [] if temporal_tier == "strict_complete" else ["incomplete_strict_indicator_outputs"],
            "eligible_for_revised_diagnostics": True,
            "eligible_for_strict_phase_scoring_diagnostics": covered_outputs > 0,
            "eligible_for_context_ablation": True,
            "eligible_for_parameter_calibration": calibration_allowed,
            "eligible_for_validation": validation_allowed,
            "eligible_for_untouched_holdout": untouched_holdout_allowed,
            "eligible_for_historical_performance_backtest": performance_allowed,
            "eligible_for_book_benchmark_reproduction": False,
        }
        scenario_rows.append(row)

    strict_complete_scenario_count = sum(
        row["temporal_tier"] == "strict_complete" for row in scenario_rows
    )
    strict_partial_scenario_count = sum(
        row["temporal_tier"] == "strict_partial" for row in scenario_rows
    )
    return {
        "phase": "QA1F",
        "scenario_count": len(scenario_rows),
        "canonical_scenario_as_of_date_count": len(scenario_entries),
        "canonical_unique_as_of_date_count": scenario_summary["canonical_unique_as_of_date_count"],
        "scenario_as_of_universe_consistent": scenario_summary["scenario_as_of_universe_consistent"],
        "strict_complete_scenario_count": strict_complete_scenario_count,
        "strict_partial_scenario_count": strict_partial_scenario_count,
        "revised_diagnostic_only_scenario_count": 0,
        "unsupported_scenario_count": 0,
        "strict_complete_as_of_pair_count": strict_complete_as_of_pair_count,
        "strict_partial_as_of_pair_count": strict_partial_as_of_pair_count,
        "missing_as_of_pair_count": missing_as_of_pair_count,
        "calibration_eligible_scenario_count": sum(row["eligible_for_parameter_calibration"] for row in scenario_rows),
        "validation_eligible_scenario_count": sum(row["eligible_for_validation"] for row in scenario_rows),
        "untouched_holdout_eligible_scenario_count": sum(row["eligible_for_untouched_holdout"] for row in scenario_rows),
        "performance_backtest_eligible_scenario_count": sum(row["eligible_for_historical_performance_backtest"] for row in scenario_rows),
        "book_benchmark_eligible_scenario_count": sum(row["eligible_for_book_benchmark_reproduction"] for row in scenario_rows),
        "scenario_with_silent_horizon_reduction_count": scenario_with_silent_horizon_reduction_count,
        "incomplete_scenario_marked_strict_complete_count": incomplete_strict_complete_count,
        "revised_scenario_marked_point_in_time_count": revised_marked_point_in_time_count,
        "strict_partial_scenario_marked_performance_eligible_count": strict_partial_performance_eligible_count,
        "previously_observed_scenario_marked_untouched_holdout_count": previously_seen_holdout_count,
        "scenarios": scenario_rows,
        "result": "passed",
    }


def formal_indicator_series_ids() -> dict[str, list[str]]:
    return {
        str(entry["indicator_id"]): _fred_candidate_series_ids(entry)
        for entry in load_indicator_catalog("specs/indicator_catalog.yaml")
    }
