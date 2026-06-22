"""End-to-end formal indicator output coverage under strict PIT inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from business_cycle.audits.scenario_as_of_inventory import (
    load_canonical_scenario_as_of_inventory,
    summarize_scenario_as_of_inventory,
)
from business_cycle.data_sources.point_in_time import (
    PointInTimeError,
    select_vintage_as_of,
    snapshot_to_frame,
)
from business_cycle.indicators.batch_scoring import score_indicator_batch
from business_cycle.indicators.catalog import load_indicator_catalog, load_indicator_scoring_specs
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError


def summarize_formal_indicator_output_coverage(
    *,
    catalog_path: str | Path = "specs/indicator_catalog.yaml",
    scenarios_path: str | Path = "specs/backtests/scenarios.yaml",
    cache_dir: str | Path = "data/raw/fred_vintages",
) -> dict[str, Any]:
    """Return formal indicator output readiness for every scenario month-end."""

    catalog_entries = load_indicator_catalog(catalog_path)
    specs = load_indicator_scoring_specs(catalog_path)
    scenario_entries = load_canonical_scenario_as_of_inventory(scenarios_path)
    scenario_summary = summarize_scenario_as_of_inventory(scenarios_path)
    total = len(catalog_entries) * len(scenario_entries)
    covered = 0
    validation_failures = 0
    full_by_indicator = {str(entry["indicator_id"]): True for entry in catalog_entries}
    partial_counts = {str(entry["indicator_id"]): 0 for entry in catalog_entries}
    duplicate_pair_ids: set[str] = set()
    seen_pair_ids: set[str] = set()

    for scenario_entry in scenario_entries:
        scenario_id = scenario_entry.scenario_id
        as_of = scenario_entry.as_of
        observations, load_failures = _load_point_in_time_observations_by_indicator(
            catalog_entries,
            cache_dir=Path(cache_dir),
            as_of=as_of,
        )
        load_failed_ids = {str(item["indicator_id"]) for item in load_failures}
        scorable_specs = {
            indicator_id: spec
            for indicator_id, spec in specs.items()
            if indicator_id not in load_failed_ids
        }
        batch = score_indicator_batch(observations, scorable_specs, as_of=as_of)
        scored_ids = {result.indicator_id for result in batch.results}
        validation_failures += len(batch.failures)
        for entry in catalog_entries:
            indicator_id = str(entry["indicator_id"])
            pair_id = f"{indicator_id}|{scenario_id}|{as_of}"
            if pair_id in seen_pair_ids:
                duplicate_pair_ids.add(pair_id)
            seen_pair_ids.add(pair_id)
            if indicator_id in scored_ids:
                covered += 1
                partial_counts[indicator_id] += 1
            else:
                full_by_indicator[indicator_id] = False

    missing = total - covered
    full_count = sum(full_by_indicator.values())
    partial_count = sum(0 < count < len(scenario_entries) for count in partial_counts.values())
    zero_count = sum(count == 0 for count in partial_counts.values())
    return {
        "formal_indicator_count": len(catalog_entries),
        "canonical_scenario_as_of_date_count": len(scenario_entries),
        "canonical_unique_as_of_date_count": scenario_summary["canonical_unique_as_of_date_count"],
        "leaf_scenario_as_of_date_count": scenario_summary["leaf_scenario_as_of_date_count"],
        "formal_indicator_scenario_as_of_date_count": scenario_summary[
            "formal_indicator_scenario_as_of_date_count"
        ],
        "unexplained_as_of_divergence_count": scenario_summary[
            "unexplained_as_of_divergence_count"
        ],
        "scenario_as_of_universe_consistent": scenario_summary[
            "scenario_as_of_universe_consistent"
        ],
        "formal_indicator_output_total_pair_count": total,
        "formal_indicator_output_covered_pair_count": covered,
        "formal_indicator_output_missing_pair_count": missing,
        "formal_indicator_output_coverage_ratio": 0.0 if total == 0 else round(covered / total, 6),
        "formal_indicator_with_full_required_horizon_count": full_count,
        "formal_indicator_with_partial_horizon_count": partial_count,
        "formal_indicator_with_zero_strict_coverage_count": zero_count,
        "formal_indicator_output_validation_failure_count": validation_failures,
        "formal_indicator_output_duplicate_pair_id_count": len(duplicate_pair_ids),
        "formal_indicator_output_counting_ready": len(duplicate_pair_ids) == 0
        and bool(scenario_summary["scenario_as_of_universe_consistent"]),
        "formal_phase_point_in_time_ready": missing == 0 and validation_failures == 0,
        "no_silent_revised_fallback": True,
        "result": "passed" if missing == 0 and validation_failures == 0 else "blocked",
    }


def _load_point_in_time_observations_by_indicator(
    entries: list[dict[str, Any]],
    *,
    cache_dir: Path,
    as_of: str,
) -> tuple[dict[str, pd.DataFrame], list[dict[str, str]]]:
    cache = PointInTimeCache(cache_dir)
    observations_by_indicator: dict[str, pd.DataFrame] = {}
    failures: list[dict[str, str]] = []
    for entry in entries:
        indicator_id = str(entry.get("indicator_id", ""))
        candidate_series = _fred_candidate_series_ids(entry)
        errors: list[str] = []
        for series_id in candidate_series:
            try:
                cached = cache.read_series(series_id)
                snapshot = select_vintage_as_of(cached.rows, series_id=series_id, as_of=as_of)
                if not snapshot.observations:
                    raise PointInTimeError("strict snapshot has no observations")
                observations_by_indicator[indicator_id] = snapshot_to_frame(snapshot)
                break
            except (PointInTimeCacheError, PointInTimeError, ValueError) as exc:
                errors.append(f"{series_id}: {exc}")
        else:
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "series_id": ",".join(candidate_series),
                    "message": "; ".join(errors),
                }
            )
    return observations_by_indicator, failures


def _fred_candidate_series_ids(entry: dict[str, Any]) -> list[str]:
    series_ids: list[str] = []
    raw_candidates = entry.get("candidate_series")
    if isinstance(raw_candidates, str):
        return [raw_candidates.strip().upper()]
    if not isinstance(raw_candidates, list):
        return series_ids
    for candidate in raw_candidates:
        if isinstance(candidate, str):
            series_ids.append(candidate.strip().upper())
        elif isinstance(candidate, dict):
            provider = str(candidate.get("provider", entry.get("provider", ""))).lower()
            series_id = candidate.get("series_id")
            if provider == "fred" and isinstance(series_id, str):
                series_ids.append(series_id.strip().upper())
    return list(dict.fromkeys(series_ids))
