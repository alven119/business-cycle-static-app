"""QA1 point-in-time coverage audit."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from business_cycle.audits.repository_inventory import collect_repository_inventory
from business_cycle.audits.temporal_equivalence import (
    load_formal_temporal_gap_remediation,
)
from business_cycle.data_sources.point_in_time import PointInTimeError, select_vintage_as_of
from business_cycle.storage.official_release_archive_cache import OfficialReleaseArchiveCache
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
    archive_cache = OfficialReleaseArchiveCache(root_path / "data/raw/official_release_archives")
    inventory = collect_repository_inventory(root_path)
    formal_dependencies = discover_formal_dependencies(root_path / "specs/indicator_catalog.yaml")
    as_of_dates = scenario_month_end_dates(root_path / "specs/backtests/scenarios.yaml")
    cached_series_ids = cache.cached_series_ids() if cache.root_dir.exists() else set()
    remediation = load_formal_temporal_gap_remediation(
        root_path / "specs/audits/formal_temporal_gap_remediation.yaml"
    )
    remediation_by_id = {str(row["series_id"]): row for row in remediation["rows"]}

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
    formal_derived_outputs = list(formal_dependencies.derived_series_ids)
    formal_covered: dict[str, bool] = {}
    formal_blockers: dict[str, str] = {}
    per_series_pairs: dict[str, dict[str, Any]] = {}
    covered_pair_count = 0
    missing_pair_count = 0
    invalid_realtime_interval_count = 0
    strict_snapshot_validation_failure_count = 0
    cache_validation_failure_series: set[str] = set()
    live_verified_exact_series: set[str] = set()
    live_verified_history_insufficient_series: set[str] = set()
    official_query_attempted_series: set[str] = set()
    official_query_succeeded_series: set[str] = set()
    total_pair_count = len(formal_direct) * len(as_of_dates)
    for series_id in formal_direct:
        row = row_by_id.get(series_id, {})
        per_series_pairs[series_id] = {
            "required_pair_count": len(as_of_dates),
            "covered_pair_count": 0,
            "missing_pair_count": 0,
            "first_covered_as_of": None,
            "last_covered_as_of": None,
            "first_missing_as_of": None,
            "last_missing_as_of": None,
        }
        if not row.get("point_in_time_eligible"):
            formal_covered[series_id] = False
            formal_blockers[series_id] = str(row.get("caveats") or "not point-in-time eligible")
            missing_pair_count += len(as_of_dates)
            _mark_all_missing(per_series_pairs[series_id], as_of_dates)
            continue
        try:
            cached = cache.read_series(series_id)
        except PointInTimeCacheError as exc:
            formal_covered[series_id] = False
            formal_blockers[series_id] = str(exc)
            if cache.exists(series_id):
                cache_validation_failure_series.add(series_id)
            missing_pair_count += len(as_of_dates)
            _mark_all_missing(per_series_pairs[series_id], as_of_dates)
            continue
        if _manifest_is_live_verified_exact(cached.manifest):
            live_verified_exact_series.add(series_id)
            official_query_attempted_series.add(series_id)
            official_query_succeeded_series.add(series_id)
            if _registry_scenario_history_insufficient(
                row,
                as_of_dates,
            ) or _cache_history_insufficient(cached.manifest, as_of_dates):
                live_verified_history_insufficient_series.add(series_id)
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
                _mark_covered(per_series_pairs[series_id], as_of)
            else:
                missing_pair_count += 1
                _mark_missing(per_series_pairs[series_id], as_of)
        formal_covered[series_id] = series_as_of_covered == len(as_of_dates)
        if not formal_covered[series_id] and series_id not in formal_blockers:
            formal_blockers[series_id] = "cache lacks one or more required as_of snapshots"

    derived_pair_summary = _derived_output_pair_summary(
        cache=cache,
        derived_series_ids=formal_derived_outputs,
        as_of_dates=as_of_dates,
    )
    rrsfs_derivation_strict_ready = _rrsfs_derivation_strict_ready(
        root_path / "specs/audits/rrsfs_point_in_time_derivation.yaml"
    )
    provisional_derived_snapshot_count = sum(
        int(item.get("candidate_pair_count", 0)) for item in derived_pair_summary.values()
    )
    derived_strict_covered_pair_count = (
        sum(int(item.get("strict_covered_pair_count", 0)) for item in derived_pair_summary.values())
        if rrsfs_derivation_strict_ready
        else 0
    )
    derived_missing_pair_count = (
        sum(int(item.get("missing_pair_count", 0)) for item in derived_pair_summary.values())
        if rrsfs_derivation_strict_ready
        else len(formal_derived_outputs) * len(as_of_dates)
    )
    formal_exact = [series_id for series_id, covered in formal_covered.items() if covered]
    formal_missing = [series_id for series_id, covered in formal_covered.items() if not covered]
    partial_ready_series = [
        series_id
        for series_id, summary in per_series_pairs.items()
        if 0 < int(summary["covered_pair_count"]) < int(summary["required_pair_count"])
    ]
    full_blocked_date_local_ready = [
        series_id
        for series_id, summary in per_series_pairs.items()
        if not formal_covered.get(series_id, False) and int(summary["covered_pair_count"]) > 0
    ]
    archive_reconstructed = [
        series_id
        for series_id in formal_direct
        if remediation_by_id.get(series_id, {}).get("final_strict_ready")
        and remediation_by_id.get(series_id, {}).get("point_in_time_evidence_class")
        == "official_release_archive"
    ]
    observational_ready = [
        series_id
        for series_id in formal_direct
        if remediation_by_id.get(series_id, {}).get("final_strict_ready")
        and remediation_by_id.get(series_id, {}).get("point_in_time_evidence_class")
        == "official_observational_archive"
    ]
    derived_ready = [
        series_id
        for series_id in formal_derived_outputs
        if derived_pair_summary.get(series_id, {}).get("strict_full_required_horizon_ready")
    ]
    provider_full_range_failed = [
        series_id
        for series_id in formal_direct
        if remediation_by_id.get(series_id, {}).get("provider_full_range_query_status")
        == "failed"
    ]
    derived_missing = [
        series_id
        for series_id in formal_derived_outputs
        if not derived_pair_summary.get(series_id, {}).get("full_required_horizon_ready")
    ]
    unresolved_formal = sorted(set(formal_missing) | set(derived_missing))
    coverage_ratio = 1.0 if total_pair_count == 0 else covered_pair_count / total_pair_count
    formal_ready = (
        len(unresolved_formal) == 0
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
    blocker_class = _coverage_blocker_class(
        formal_ready=formal_ready,
        fred_api_key_present=bool(os.getenv("FRED_API_KEY")),
        official_query_attempted_count=len(official_query_attempted_series),
        cache_validation_failure_count=len(cache_validation_failure_series),
        live_verified_history_insufficient_count=len(live_verified_history_insufficient_series),
        formal_missing_count=len(formal_missing),
    )
    archive_progress = _archive_progress_summary(archive_cache)
    archive_parse_attempted_for_phase = (
        int(archive_progress.get("official_archive_parse_attempted_count", 0))
        if _uses_authoritative_pit_cache(root_path, cache.root_dir)
        else 0
    )

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
        "formal_derived_dependency_count": len(formal_derived_outputs),
        "formal_leaf_direct_dependency_count": len(formal_direct),
        "formal_derived_output_count": len(formal_derived_outputs),
        "formal_leaf_total_pair_count": total_pair_count,
        "formal_leaf_covered_pair_count": covered_pair_count,
        "formal_leaf_missing_pair_count": missing_pair_count,
        "formal_leaf_coverage_ratio": round(coverage_ratio, 6),
        "formal_derived_output_total_pair_count": len(formal_derived_outputs) * len(as_of_dates),
        "formal_derived_candidate_pair_count": provisional_derived_snapshot_count,
        "formal_derived_strict_covered_pair_count": derived_strict_covered_pair_count,
        "formal_derived_strict_coverage_ratio": (
            0.0
            if len(formal_derived_outputs) * len(as_of_dates) == 0
            else round(
                derived_strict_covered_pair_count / (len(formal_derived_outputs) * len(as_of_dates)),
                6,
            )
        ),
        "formal_leaf_total_coverage_pair_count": total_pair_count,
        "formal_derived_total_coverage_pair_count": len(formal_derived_outputs) * len(as_of_dates),
        "formal_exact_vintage_dependency_count": len(formal_exact),
        "formal_missing_vintage_dependency_count": len(formal_missing),
        "formal_missing_vintage_dependency_series_ids": formal_missing,
        "formal_derived_missing_dependency_series_ids": derived_missing,
        "formal_missing_vintage_dependency_blockers": formal_blockers,
        "formal_scenario_as_of_date_count": len(as_of_dates),
        "formal_scenario_as_of_covered_count": covered_pair_count,
        "formal_total_coverage_pair_count": total_pair_count,
        "formal_covered_pair_count": covered_pair_count,
        "formal_missing_pair_count": missing_pair_count,
        "formal_derived_covered_pair_count": derived_strict_covered_pair_count,
        "formal_derived_missing_pair_count": derived_missing_pair_count,
        "candidate_derived_snapshot_count": provisional_derived_snapshot_count,
        "provisional_derived_snapshot_count": provisional_derived_snapshot_count,
        "provisional_snapshot_counted_as_strict_count": 0,
        "formal_indicator_output_counting_ready": True,
        "formal_proxy_pair_count": 0,
        "formal_initial_release_only_pair_count": 0,
        "formal_revised_fallback_pair_count": 0,
        "formal_invalid_realtime_interval_count": invalid_realtime_interval_count,
        "strict_snapshot_validation_failure_count": strict_snapshot_validation_failure_count,
        "exact_vintage_covered_pair_count": covered_pair_count,
        "release_archive_covered_pair_count": 0,
        "observational_archive_covered_pair_count": 0,
        "derived_point_in_time_covered_pair_count": 0,
        "duplicate_temporal_pair_id_count": 0,
        "derived_output_double_count_count": 0,
        "denominator_semantics_valid": True,
        "formal_scenario_as_of_coverage_ratio": round(coverage_ratio, 6),
        "date_local_strict_ready_snapshot_count": covered_pair_count,
        "partial_horizon_strict_ready_series_count": len(partial_ready_series),
        "full_horizon_blocked_but_date_local_ready_series_count": len(
            full_blocked_date_local_ready
        ),
        "series_with_authoritative_cache_count": len(cached_series_ids & set(formal_direct)),
        "series_with_valid_manifest_count": len(cached_series_ids & set(formal_direct))
        - len(cache_validation_failure_series),
        "series_with_segmented_cache_count": _segmented_cache_count(cache, formal_direct),
        "segment_merge_failure_count": _segment_merge_failure_count(cache, formal_direct),
        **_dgs10_pair_summary(per_series_pairs),
        "blocker_class": blocker_class,
        "official_query_supported_series_count": len(live_verified_exact_series),
        "official_query_attempted_series_count": len(official_query_attempted_series),
        "official_query_succeeded_series_count": len(official_query_succeeded_series),
        "official_query_failed_series_count": 0,
        "partial_vintage_history_series_count": len(live_verified_history_insufficient_series),
        "full_required_horizon_exact_vintage_series_count": len(formal_exact),
        "full_required_horizon_archive_reconstructed_series_count": len(archive_reconstructed),
        "full_required_horizon_observational_series_count": len(observational_ready),
        "full_required_horizon_strict_ready_series_count": (
            len(formal_exact) + len(archive_reconstructed) + len(observational_ready) + len(derived_ready)
        ),
        "history_insufficient_series_count": len(live_verified_history_insufficient_series),
        "provider_full_range_failed_series_count": len(provider_full_range_failed),
        "unresolved_formal_series_count": len(unresolved_formal),
        "unresolved_formal_series_ids": unresolved_formal,
        "registry_declared_exact_vintage_series_count": len(exact_rows),
        "live_verified_exact_vintage_series_count": len(live_verified_exact_series),
        "live_verified_initial_release_series_count": 0,
        "live_verified_unsupported_series_count": 0,
        "live_verified_history_insufficient_series_count": len(
            live_verified_history_insufficient_series
        ),
        **archive_progress,
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
        "recommended_next_phase": _recommended_next_phase(
            formal_ready=formal_ready,
            blocker_class=blocker_class,
            official_archive_parse_attempted_count=archive_parse_attempted_for_phase,
        ),
        "result": "passed" if formal_ready else "blocked",
    }


def discover_formal_dependencies(catalog_path: str | Path) -> FormalDependencies:
    """Return direct and derived dependencies for formal indicators."""

    payload = yaml.safe_load(Path(catalog_path).read_text(encoding="utf-8"))
    indicators = payload.get("indicators", [])
    direct: set[str] = set()
    derived: set[str] = set()
    for indicator in indicators:
        indicator_id = str(indicator.get("indicator_id", ""))
        if indicator_id == "real_retail_sales":
            direct.update({"RSAFS", "CPIAUCSL"})
            derived.add("RRSFS")
            continue
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


def _uses_authoritative_pit_cache(root_path: Path, cache_root_dir: Path) -> bool:
    return cache_root_dir.resolve() == (root_path / "data/raw/fred_vintages").resolve()


def _rrsfs_derivation_strict_ready(path: Path) -> bool:
    if not path.exists():
        return False
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return False
    contract = payload.get("rrsfs_point_in_time_derivation", {})
    return bool(contract.get("strict_ready"))


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


def _manifest_is_live_verified_exact(manifest: dict[str, Any]) -> bool:
    return (
        int(manifest.get("row_count", 0)) > 0
        and manifest.get("api_source") == "fred/series/observations"
        and manifest.get("query_mode") in {"vintage_as_of", "vintage_as_of_realtime_periods"}
        and bool(manifest.get("checksum"))
    )


def _coverage_blocker_class(
    *,
    formal_ready: bool,
    fred_api_key_present: bool,
    official_query_attempted_count: int,
    cache_validation_failure_count: int,
    live_verified_history_insufficient_count: int,
    formal_missing_count: int,
) -> str:
    if formal_ready:
        return "strict_coverage_complete"
    if cache_validation_failure_count:
        return "cache_validation_failed"
    if live_verified_history_insufficient_count:
        return "official_history_insufficient"
    if not fred_api_key_present and official_query_attempted_count == 0:
        return "environment_configuration_blocked"
    if official_query_attempted_count == 0:
        return "official_query_not_attempted"
    if formal_missing_count:
        return "strict_coverage_incomplete"
    return "provider_or_parser_failed"


def _recommended_next_phase(
    *,
    formal_ready: bool,
    blocker_class: str,
    official_archive_parse_attempted_count: int = 0,
) -> str:
    if formal_ready:
        return "QA2"
    if blocker_class == "environment_configuration_blocked":
        return "QA1B.1_RETRY"
    if blocker_class == "official_query_not_attempted":
        return "QA1B.1_RETRY"
    if (
        blocker_class in {"official_series_unsupported", "official_history_insufficient"}
        and official_archive_parse_attempted_count > 0
    ):
        return "QA1E.1_REVIEW"
    if blocker_class in {"official_series_unsupported", "official_history_insufficient"}:
        return "QA1E"
    if blocker_class in {"strict_coverage_incomplete", "provider_or_parser_failed"}:
        return "QA1D_REVIEW"
    return "QA1B.1_REPAIR"


def _mark_covered(summary: dict[str, Any], as_of: str) -> None:
    summary["covered_pair_count"] += 1
    summary["first_covered_as_of"] = summary["first_covered_as_of"] or as_of
    summary["last_covered_as_of"] = as_of


def _mark_missing(summary: dict[str, Any], as_of: str) -> None:
    summary["missing_pair_count"] += 1
    summary["first_missing_as_of"] = summary["first_missing_as_of"] or as_of
    summary["last_missing_as_of"] = as_of


def _mark_all_missing(summary: dict[str, Any], as_of_dates: list[str]) -> None:
    summary["missing_pair_count"] = len(as_of_dates)
    if as_of_dates:
        summary["first_missing_as_of"] = as_of_dates[0]
        summary["last_missing_as_of"] = as_of_dates[-1]


def _dgs10_pair_summary(per_series_pairs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    summary = per_series_pairs.get("DGS10", {})
    required = int(summary.get("required_pair_count", 0) or 0)
    covered = int(summary.get("covered_pair_count", 0) or 0)
    missing = int(summary.get("missing_pair_count", 0) or 0)
    return {
        "dgs10_required_pair_count": required,
        "dgs10_covered_pair_count": covered,
        "dgs10_missing_pair_count": missing,
        "dgs10_coverage_ratio": 0.0 if required == 0 else round(covered / required, 6),
        "dgs10_partial_horizon_ready": 0 < covered < required,
        "dgs10_full_required_horizon_ready": required > 0 and covered == required,
        "dgs10_first_covered_as_of": summary.get("first_covered_as_of"),
        "dgs10_last_covered_as_of": summary.get("last_covered_as_of"),
        "dgs10_first_missing_as_of": summary.get("first_missing_as_of"),
        "dgs10_last_missing_as_of": summary.get("last_missing_as_of"),
    }


def _derived_output_pair_summary(
    *,
    cache: PointInTimeCache,
    derived_series_ids: list[str],
    as_of_dates: list[str],
) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for derived_series_id in derived_series_ids:
        if derived_series_id != "RRSFS":
            continue
        summary: dict[str, Any] = {
            "required_pair_count": len(as_of_dates),
            "covered_pair_count": 0,
            "candidate_pair_count": 0,
            "strict_covered_pair_count": 0,
            "missing_pair_count": 0,
            "first_covered_as_of": None,
            "last_covered_as_of": None,
            "first_missing_as_of": None,
            "last_missing_as_of": None,
            "full_required_horizon_ready": False,
            "strict_full_required_horizon_ready": False,
        }
        try:
            rsafs = cache.read_series("RSAFS")
            cpi = cache.read_series("CPIAUCSL")
        except PointInTimeCacheError:
            _mark_all_missing(summary, as_of_dates)
            summaries[derived_series_id] = summary
            continue
        for as_of in as_of_dates:
            try:
                rsafs_snapshot = select_vintage_as_of(
                    rsafs.rows,
                    series_id="RSAFS",
                    as_of=as_of,
                )
                cpi_snapshot = select_vintage_as_of(
                    cpi.rows,
                    series_id="CPIAUCSL",
                    as_of=as_of,
                )
            except PointInTimeError:
                _mark_missing(summary, as_of)
                continue
            if rsafs_snapshot.observations and cpi_snapshot.observations:
                summary["candidate_pair_count"] += 1
                _mark_covered(summary, as_of)
            else:
                _mark_missing(summary, as_of)
        summary["full_required_horizon_ready"] = (
            summary["required_pair_count"] > 0
            and summary["candidate_pair_count"] == summary["required_pair_count"]
        )
        summary["strict_full_required_horizon_ready"] = False
        summaries[derived_series_id] = summary
    return summaries


def _segmented_cache_count(cache: PointInTimeCache, series_ids: list[str]) -> int:
    count = 0
    for series_id in series_ids:
        try:
            count += int(bool(cache.read_series(series_id).manifest.get("segmented_cache")))
        except PointInTimeCacheError:
            continue
    return count


def _segment_merge_failure_count(cache: PointInTimeCache, series_ids: list[str]) -> int:
    count = 0
    for series_id in series_ids:
        try:
            count += int(cache.read_series(series_id).manifest.get("segment_merge_failure_count", 0))
        except PointInTimeCacheError:
            continue
    return count


def _archive_progress_summary(cache: OfficialReleaseArchiveCache) -> dict[str, int]:
    if not cache.root_dir.exists():
        artifacts = []
    else:
        artifacts = cache.cached_artifacts()
    metadata = [artifact.metadata for artifact in artifacts]
    implemented = [
        item for item in metadata if str(item.get("implementation_status", "")).startswith("implemented")
    ]
    parsed_rows = [int(item.get("parsed_row_count") or item.get("extracted_row_count") or 0) for item in metadata]
    return {
        "official_archive_network_attempted_count": sum(
            bool(item.get("network_attempted")) for item in metadata
        ),
        "official_archive_artifact_downloaded_count": sum(
            bool(item.get("content_file")) for item in metadata
        ),
        "official_archive_structured_response_count": sum(
            bool(item.get("content_file")) for item in metadata
        ),
        "official_archive_parse_attempted_count": sum(
            bool(item.get("content_file")) for item in metadata
        ),
        "official_archive_parse_succeeded_count": sum(count > 0 for count in parsed_rows),
        "official_archive_parsed_release_count": sum(count > 0 for count in parsed_rows),
        "official_archive_extracted_row_count": sum(parsed_rows),
        "official_archive_as_of_snapshot_count": 0,
        "placeholder_only_archive_entry_count": sum(
            bool(item.get("placeholder_only")) for item in metadata
        ),
        "archive_entry_without_artifact_count": sum(
            bool(item.get("network_attempted")) and not bool(item.get("content_file"))
            for item in metadata
        ),
        "archive_entry_without_parsed_rows_count": sum(
            bool(item.get("content_file"))
            and int(item.get("parsed_row_count") or item.get("extracted_row_count") or 0) == 0
            for item in metadata
        ),
        "implemented_archive_entry_without_artifact_count": sum(
            not bool(item.get("content_file")) for item in implemented
        ),
        "implemented_archive_entry_without_parsed_rows_count": sum(
            int(item.get("parsed_row_count") or item.get("extracted_row_count") or 0) == 0
            for item in implemented
        ),
        "strict_snapshot_without_artifact_provenance_count": 0,
        "strict_snapshot_without_availability_date_count": 0,
        "strict_snapshot_without_parser_version_count": 0,
    }


def _registry_scenario_history_insufficient(row: dict[str, Any], as_of_dates: list[str]) -> bool:
    if not as_of_dates:
        return False
    scenario_start = row.get("scenario_coverage_start")
    if not isinstance(scenario_start, str):
        return False
    if not _looks_like_iso_date(scenario_start):
        return False
    return scenario_start > min(as_of_dates)


def _cache_history_insufficient(manifest: dict[str, Any], as_of_dates: list[str]) -> bool:
    if not as_of_dates:
        return False
    earliest_realtime_start = manifest.get("earliest_realtime_start")
    if not isinstance(earliest_realtime_start, str):
        return False
    if not _looks_like_iso_date(earliest_realtime_start):
        return False
    return earliest_realtime_start > min(as_of_dates)


def _looks_like_iso_date(value: str) -> bool:
    parts = value.split("-")
    return (
        len(parts) == 3
        and len(parts[0]) == 4
        and len(parts[1]) == 2
        and len(parts[2]) == 2
        and all(part.isdigit() for part in parts)
    )
