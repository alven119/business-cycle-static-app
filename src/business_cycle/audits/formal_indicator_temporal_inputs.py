"""Explain strict temporal inputs used by formal indicator scoring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from business_cycle.data_sources.point_in_time import (
    PointInTimeError,
    PointInTimeSnapshot,
    select_vintage_as_of,
    snapshot_to_frame,
)
from business_cycle.indicators.batch_scoring import score_indicator_batch
from business_cycle.indicators.catalog import load_indicator_catalog, load_indicator_scoring_specs
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError


@dataclass(frozen=True)
class TemporalInputSelection:
    """One selected temporal input for an indicator."""

    indicator_id: str
    as_of: str
    dependency_series_ids: tuple[str, ...]
    selected_dependency_path: str
    selected_dependency_class: str
    direct_or_derived: str
    temporal_evidence_class: str | None
    source_artifact_ids: tuple[str, ...]
    selected_observation_dates: tuple[str, ...]
    availability_dates: tuple[str, ...]
    transformation_id: str | None
    strict_output_ready: bool
    missing_dependencies: tuple[str, ...]
    proxy_used: bool
    revised_fallback_used: bool


def explain_formal_indicator_temporal_inputs(
    *,
    as_of: str,
    catalog_path: str | Path = "specs/indicator_catalog.yaml",
    cache_dir: str | Path = "data/raw/fred_vintages",
) -> dict[str, Any]:
    """Return strict temporal input provenance for each formal indicator at one as-of date."""

    catalog_entries = load_indicator_catalog(catalog_path)
    specs = load_indicator_scoring_specs(catalog_path)
    cache = PointInTimeCache(cache_dir)
    selections: list[TemporalInputSelection] = []
    observations_by_indicator: dict[str, pd.DataFrame] = {}
    selected_indicator_ids: set[str] = set()

    for entry in catalog_entries:
        indicator_id = str(entry.get("indicator_id", ""))
        dependency_series_ids = tuple(_fred_candidate_series_ids(entry))
        selection = _select_indicator_input(
            indicator_id=indicator_id,
            dependency_series_ids=dependency_series_ids,
            transformation_id=str(entry.get("score_method") or ""),
            as_of=as_of,
            cache=cache,
        )
        selections.append(selection)
        if selection.strict_output_ready and selection.source_artifact_ids:
            selected_indicator_ids.add(indicator_id)
            selected_series = selection.source_artifact_ids[0].split(":", maxsplit=3)[1]
            cached = cache.read_series(selected_series)
            snapshot = select_vintage_as_of(cached.rows, series_id=selected_series, as_of=as_of)
            observations_by_indicator[indicator_id] = snapshot_to_frame(snapshot)

    scorable_specs = {
        indicator_id: spec
        for indicator_id, spec in specs.items()
        if indicator_id in selected_indicator_ids
    }
    batch = score_indicator_batch(observations_by_indicator, scorable_specs, as_of=as_of)
    scored_ids = {result.indicator_id for result in batch.results}
    normalized: list[dict[str, Any]] = []
    strict_score_without_dependency = 0
    strict_score_without_provenance = 0
    ambiguity_count = 0
    proxy_count = 0
    revised_fallback_count = 0

    for selection in selections:
        ready = selection.indicator_id in scored_ids
        item = _selection_to_dict(selection, strict_output_ready=ready)
        normalized.append(item)
        if ready and not selection.source_artifact_ids:
            strict_score_without_dependency += 1
        if ready and (
            not selection.temporal_evidence_class
            or not selection.selected_observation_dates
            or not selection.availability_dates
        ):
            strict_score_without_provenance += 1
        if _has_direct_derived_ambiguity(item):
            ambiguity_count += 1
        proxy_count += int(selection.proxy_used)
        revised_fallback_count += int(selection.revised_fallback_used)

    return {
        "as_of": as_of,
        "formal_indicator_count": len(catalog_entries),
        "scored_indicator_count": len(scored_ids),
        "failed_indicator_count": len(catalog_entries) - len(scored_ids),
        "strict_score_without_covered_dependency_count": strict_score_without_dependency,
        "strict_score_without_temporal_provenance_count": strict_score_without_provenance,
        "direct_derived_dependency_ambiguity_count": ambiguity_count,
        "proxy_used_count": proxy_count,
        "revised_fallback_used_count": revised_fallback_count,
        "indicators": normalized,
    }


def _select_indicator_input(
    *,
    indicator_id: str,
    dependency_series_ids: tuple[str, ...],
    transformation_id: str,
    as_of: str,
    cache: PointInTimeCache,
) -> TemporalInputSelection:
    errors: list[str] = []
    for series_id in dependency_series_ids:
        try:
            cached = cache.read_series(series_id)
            snapshot = select_vintage_as_of(cached.rows, series_id=series_id, as_of=as_of)
        except (PointInTimeCacheError, PointInTimeError, ValueError) as exc:
            errors.append(f"{series_id}: {exc}")
            continue
        if not snapshot.observations:
            errors.append(f"{series_id}: strict snapshot has no observations")
            continue
        return _ready_selection(
            indicator_id=indicator_id,
            dependency_series_ids=dependency_series_ids,
            transformation_id=transformation_id,
            snapshot=snapshot,
            manifest=cached.manifest,
        )
    return TemporalInputSelection(
        indicator_id=indicator_id,
        as_of=as_of,
        dependency_series_ids=dependency_series_ids,
        selected_dependency_path="none",
        selected_dependency_class="missing_strict_dependency",
        direct_or_derived="none",
        temporal_evidence_class=None,
        source_artifact_ids=(),
        selected_observation_dates=(),
        availability_dates=(),
        transformation_id=transformation_id,
        strict_output_ready=False,
        missing_dependencies=dependency_series_ids or tuple(errors),
        proxy_used=False,
        revised_fallback_used=False,
    )


def _ready_selection(
    *,
    indicator_id: str,
    dependency_series_ids: tuple[str, ...],
    transformation_id: str,
    snapshot: PointInTimeSnapshot,
    manifest: dict[str, Any],
) -> TemporalInputSelection:
    latest = snapshot.observations[-1]
    checksum = str(manifest.get("checksum") or "missing_checksum")
    return TemporalInputSelection(
        indicator_id=indicator_id,
        as_of=snapshot.as_of.isoformat(),
        dependency_series_ids=dependency_series_ids,
        selected_dependency_path=f"direct_exact_vintage:{snapshot.series_id}",
        selected_dependency_class="fred_candidate_series",
        direct_or_derived="direct",
        temporal_evidence_class="exact_vintage_interval",
        source_artifact_ids=(f"pit_cache:{snapshot.series_id}:{checksum}",),
        selected_observation_dates=(latest.observation_date.isoformat(),),
        availability_dates=(latest.realtime_start.isoformat(),),
        transformation_id=transformation_id,
        strict_output_ready=True,
        missing_dependencies=(),
        proxy_used=False,
        revised_fallback_used=False,
    )


def _selection_to_dict(
    selection: TemporalInputSelection,
    *,
    strict_output_ready: bool,
) -> dict[str, Any]:
    return {
        "indicator_id": selection.indicator_id,
        "as_of": selection.as_of,
        "dependency_series_ids": list(selection.dependency_series_ids),
        "selected_dependency_path": selection.selected_dependency_path,
        "selected_dependency_class": selection.selected_dependency_class,
        "direct_or_derived": selection.direct_or_derived,
        "temporal_evidence_class": selection.temporal_evidence_class,
        "source_artifact_ids": list(selection.source_artifact_ids),
        "selected_observation_dates": list(selection.selected_observation_dates),
        "availability_dates": list(selection.availability_dates),
        "transformation_id": selection.transformation_id,
        "strict_output_ready": strict_output_ready,
        "missing_dependencies": list(selection.missing_dependencies),
        "proxy_used": selection.proxy_used,
        "revised_fallback_used": selection.revised_fallback_used,
    }


def _has_direct_derived_ambiguity(item: dict[str, Any]) -> bool:
    return item["direct_or_derived"] == "hybrid_unresolved"


def _fred_candidate_series_ids(entry: dict[str, Any]) -> list[str]:
    series_ids: list[str] = []
    raw_candidates = entry.get("candidate_series")
    if isinstance(raw_candidates, str):
        return [raw_candidates.strip().upper()]
    if isinstance(raw_candidates, dict):
        series_id = _candidate_series_id_if_fred(
            raw_candidates,
            default_provider=str(entry.get("provider", "")),
        )
        return [] if series_id is None else [series_id]
    if not isinstance(raw_candidates, list):
        return series_ids
    for candidate in raw_candidates:
        if isinstance(candidate, str):
            series_ids.append(candidate.strip().upper())
        elif isinstance(candidate, dict):
            series_id = _candidate_series_id_if_fred(
                candidate,
                default_provider=str(entry.get("provider", "")),
            )
            if series_id is not None:
                series_ids.append(series_id)
    return list(dict.fromkeys(series_ids))


def _candidate_series_id_if_fred(candidate: dict[str, Any], *, default_provider: str) -> str | None:
    provider = str(candidate.get("provider", default_provider)).lower()
    series_id = candidate.get("series_id")
    if provider != "fred" or not isinstance(series_id, str):
        return None
    return series_id.strip().upper()
