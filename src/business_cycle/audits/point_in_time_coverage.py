"""QA1 point-in-time coverage audit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from business_cycle.audits.repository_inventory import collect_repository_inventory
from business_cycle.data_sources.point_in_time import PointInTimeError, select_vintage_as_of
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError


class PointInTimeCoverageError(ValueError):
    """Raised when point-in-time audit inputs are invalid."""


@dataclass(frozen=True)
class FormalDependencies:
    """Formal indicator dependency inventory."""

    formal_indicator_count: int
    direct_series_ids: tuple[str, ...]
    derived_series_ids: tuple[str, ...]


def summarize_point_in_time_coverage(
    *,
    root: str | Path = ".",
    cache_dir: str | Path = "data/raw/fred_vintages",
) -> dict[str, Any]:
    """Summarize QA1 point-in-time metadata and cache coverage."""

    root_path = Path(root)
    registry = _load_registry(root_path / "specs/common/series_release_lag_registry.yaml")
    rows = registry["series"]
    cache = PointInTimeCache(root_path / cache_dir)
    inventory = collect_repository_inventory(root_path)
    formal_dependencies = discover_formal_dependencies(root_path / "specs/indicator_catalog.yaml")
    as_of_dates = scenario_month_end_dates(root_path / "specs/backtests/scenarios.yaml")
    cached_series_ids = cache.cached_series_ids() if cache.root_dir.exists() else set()

    row_by_id = {str(row["series_id"]): row for row in rows}
    metadata_complete = [row for row in rows if _row_metadata_complete(row)]
    exact_rows = [row for row in rows if row.get("temporal_status") == "exact_vintage_ready"]
    initial_rows = [row for row in rows if row.get("temporal_status") == "initial_release_only"]
    proxy_rows = [row for row in rows if row.get("temporal_status") == "proxy_only"]
    unsupported_rows = [row for row in rows if row.get("temporal_status") == "unsupported"]
    release_lag_proxy_misclassified = [
        row
        for row in rows
        if row.get("availability_mode") == "release_lag_proxy"
        and bool(row.get("point_in_time_eligible"))
    ]

    formal_direct = list(formal_dependencies.direct_series_ids)
    formal_covered: dict[str, bool] = {}
    formal_blockers: dict[str, str] = {}
    covered_pair_count = 0
    missing_pair_count = 0
    invalid_realtime_interval_count = 0
    strict_snapshot_validation_failure_count = 0
    total_pair_count = len(formal_direct) * len(as_of_dates)
    for series_id in formal_direct:
        row = row_by_id.get(series_id, {})
        if not row.get("point_in_time_eligible"):
            formal_covered[series_id] = False
            formal_blockers[series_id] = str(row.get("caveats") or "not point-in-time eligible")
            missing_pair_count += len(as_of_dates)
            continue
        try:
            cached = cache.read_series(series_id)
        except PointInTimeCacheError as exc:
            formal_covered[series_id] = False
            formal_blockers[series_id] = str(exc)
            missing_pair_count += len(as_of_dates)
            continue
        series_as_of_covered = 0
        for as_of in as_of_dates:
            try:
                snapshot = select_vintage_as_of(
                    cached.rows,
                    series_id=series_id,
                    as_of=as_of,
                    availability_precision=str(row.get("availability_precision", "unknown")),
                )
            except PointInTimeError as exc:
                formal_blockers[series_id] = str(exc)
                invalid_realtime_interval_count += 1
                strict_snapshot_validation_failure_count += 1
                missing_pair_count += 1
                continue
            if snapshot.observations:
                series_as_of_covered += 1
                covered_pair_count += 1
            else:
                missing_pair_count += 1
        formal_covered[series_id] = series_as_of_covered == len(as_of_dates)
        if not formal_covered[series_id] and series_id not in formal_blockers:
            formal_blockers[series_id] = "cache lacks one or more required as_of snapshots"

    formal_exact = [series_id for series_id, covered in formal_covered.items() if covered]
    formal_missing = [series_id for series_id, covered in formal_covered.items() if not covered]
    coverage_ratio = 1.0 if total_pair_count == 0 else covered_pair_count / total_pair_count
    formal_ready = (
        len(formal_missing) == 0
        and total_pair_count > 0
        and covered_pair_count == total_pair_count
        and not release_lag_proxy_misclassified
        and strict_snapshot_validation_failure_count == 0
    )
    exact_experimental = [
        item
        for item in inventory["items"]
        if item["inventory_type"] == "experimental_indicator"
        and all(
            row_by_id.get(series_id, {}).get("point_in_time_eligible")
            for series_id in item.get("referenced_series_ids", [])
        )
    ]
    experimental_count = inventory["discovered_experimental_indicator_count"] or 1

    return {
        "discovered_unique_series_count": inventory["discovered_unique_series_count"],
        "availability_metadata_complete_count": len(metadata_complete),
        "exact_vintage_supported_series_count": len(exact_rows),
        "initial_release_only_series_count": len(initial_rows),
        "release_lag_proxy_series_count": len(proxy_rows),
        "unsupported_series_count": len(unsupported_rows),
        "cached_series_count": len(cached_series_ids),
        "formal_indicator_count": formal_dependencies.formal_indicator_count,
        "formal_direct_dependency_count": len(formal_direct),
        "formal_derived_dependency_count": len(formal_dependencies.derived_series_ids),
        "formal_exact_vintage_dependency_count": len(formal_exact),
        "formal_missing_vintage_dependency_count": len(formal_missing),
        "formal_missing_vintage_dependency_series_ids": formal_missing,
        "formal_missing_vintage_dependency_blockers": formal_blockers,
        "formal_scenario_as_of_date_count": len(as_of_dates),
        "formal_scenario_as_of_covered_count": covered_pair_count,
        "formal_total_coverage_pair_count": total_pair_count,
        "formal_covered_pair_count": covered_pair_count,
        "formal_missing_pair_count": missing_pair_count,
        "formal_proxy_pair_count": 0,
        "formal_initial_release_only_pair_count": 0,
        "formal_revised_fallback_pair_count": 0,
        "formal_invalid_realtime_interval_count": invalid_realtime_interval_count,
        "strict_snapshot_validation_failure_count": strict_snapshot_validation_failure_count,
        "formal_scenario_as_of_coverage_ratio": round(coverage_ratio, 6),
        "experimental_exact_vintage_coverage_ratio": round(
            len(exact_experimental) / experimental_count,
            6,
        ),
        "point_in_time_selector_ready": True,
        "formal_phase_point_in_time_ready": formal_ready,
        "all_experimental_point_in_time_ready": len(exact_experimental) == experimental_count,
        "golden_benchmark_point_in_time_ready": False,
        "no_silent_revised_fallback": True,
        "release_lag_proxy_misclassified_as_point_in_time_count": len(
            release_lag_proxy_misclassified
        ),
        "availability_precision_day_count": len(
            [row for row in rows if row.get("availability_precision") == "day"]
        ),
        "availability_precision_unknown_count": len(
            [row for row in rows if row.get("availability_precision") == "unknown"]
        ),
        "alfred_ingestion_lag_caveat_present": any(
            "Metadata completeness does not imply local vintage cache coverage"
            in str(row.get("caveats", ""))
            for row in rows
        ),
        "point_in_time_backtest_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "recommended_next_phase": "QA2" if formal_ready else "QA1C",
        "result": "passed" if formal_ready else "blocked",
    }


def discover_formal_dependencies(catalog_path: str | Path) -> FormalDependencies:
    """Return direct and derived dependencies for formal indicators."""

    payload = yaml.safe_load(Path(catalog_path).read_text(encoding="utf-8"))
    indicators = payload.get("indicators", [])
    direct: set[str] = set()
    derived: set[str] = set()
    for indicator in indicators:
        for series_id in _extract_series_ids(indicator):
            if series_id.startswith("derived:"):
                derived.add(series_id)
            else:
                direct.add(series_id)
    return FormalDependencies(
        formal_indicator_count=len(indicators),
        direct_series_ids=tuple(sorted(direct)),
        derived_series_ids=tuple(sorted(derived)),
    )


def scenario_month_end_dates(scenarios_path: str | Path) -> list[str]:
    """Return all monthly end-of-day as-of dates across scenario windows."""

    payload = yaml.safe_load(Path(scenarios_path).read_text(encoding="utf-8"))
    scenarios = payload.get("scenarios", [])
    dates: set[str] = set()
    for scenario in scenarios:
        start = pd.Timestamp(str(scenario["window_start"]))
        end = pd.Timestamp(str(scenario["window_end"]))
        for timestamp in pd.date_range(start=start, end=end, freq="ME"):
            dates.add(timestamp.date().isoformat())
    return sorted(dates)


def _load_registry(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(
        payload.get("series_release_lag_registry"), dict
    ):
        raise PointInTimeCoverageError("series_release_lag_registry root is required")
    registry = payload["series_release_lag_registry"]
    if not isinstance(registry.get("series"), list):
        raise PointInTimeCoverageError("series_release_lag_registry.series must be a list")
    return registry


def _row_metadata_complete(row: dict[str, Any]) -> bool:
    required = (
        "series_id",
        "source",
        "frequency",
        "availability_mode",
        "availability_precision",
        "release_lag_rule",
        "vintage_query_supported",
        "initial_release_query_supported",
        "temporal_status",
        "point_in_time_eligible",
        "known_revision_behavior",
        "official_metadata_source",
        "caveats",
    )
    return all(key in row and row[key] not in ("", None) for key in required)


def _extract_series_ids(value: Any) -> set[str]:
    series_ids: set[str] = set()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("series_id"), str):
                series_ids.add(node["series_id"].strip().upper())
            if isinstance(node.get("preferred_series"), str):
                series_ids.add(node["preferred_series"].strip().upper())
            if isinstance(node.get("candidate_fred_series"), list):
                for candidate in node["candidate_fred_series"]:
                    if isinstance(candidate, str):
                        series_ids.add(candidate.strip().upper())
            for item in node.values():
                visit(item)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(value)
    return series_ids
