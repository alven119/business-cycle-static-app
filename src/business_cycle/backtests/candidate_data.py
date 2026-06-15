"""Experimental candidate FRED cache updater."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from business_cycle import data_sources
from business_cycle.backtests.candidate_indicators import (
    RecessionConfirmationCandidateSpec,
    load_recession_confirmation_candidate_indicators,
)
from business_cycle.storage.raw_store import RawCsvStore


class CandidateFredProvider(Protocol):
    """Provider protocol used by candidate data updater tests."""

    def fetch_series_observations(self, series_id: str) -> list[data_sources.SeriesObservation]:
        """Fetch one FRED series."""


@dataclass(frozen=True)
class CandidateDataUpdateResult:
    """One candidate series update result."""

    series_id: str
    status: str
    cache_path: str
    message: str


def candidate_fred_series_ids(spec: RecessionConfirmationCandidateSpec) -> list[str]:
    """Collect unique candidate FRED series ids, including derived indicator inputs."""

    series_ids: list[str] = []
    seen: set[str] = set()
    for indicator in spec.indicators:
        for series_id in indicator.get("candidate_fred_series", []):
            clean = str(series_id).strip().upper()
            if clean and clean not in seen:
                seen.add(clean)
                series_ids.append(clean)
    return series_ids


def update_candidate_fred_cache(
    *,
    spec_path: str | Path = "specs/backtests/recession_confirmation_candidate_indicators.yaml",
    raw_dir: str | Path = "data/raw",
    provider: CandidateFredProvider | None = None,
    dry_run: bool = False,
    force_refresh: bool = False,
    no_api: bool = False,
) -> dict:
    """Update local raw FRED cache for recession-confirmation candidate series."""

    spec = load_recession_confirmation_candidate_indicators(spec_path)
    store = RawCsvStore(raw_dir)
    series_ids = candidate_fred_series_ids(spec)
    results: list[CandidateDataUpdateResult] = []

    if dry_run or no_api:
        for series_id in series_ids:
            cache_path = store.path_for("fred", series_id)
            status = "cached" if cache_path.exists() else "missing"
            message = "dry_run" if dry_run else "no_api"
            results.append(CandidateDataUpdateResult(series_id, status, str(cache_path), message))
        return _summary(series_ids, results, store, dry_run=dry_run, no_api=no_api)

    active_provider = provider or data_sources.FredProvider()
    if hasattr(active_provider, "require_api_key"):
        active_provider.require_api_key()  # type: ignore[attr-defined]

    for series_id in series_ids:
        cache_path = store.path_for("fred", series_id)
        if cache_path.exists() and not force_refresh:
            results.append(CandidateDataUpdateResult(series_id, "cached", str(cache_path), "cache_exists"))
            continue
        try:
            observations = active_provider.fetch_series_observations(series_id)
            written_path = store.write_observations("fred", series_id, observations)
        except data_sources.FredProviderError as exc:
            results.append(CandidateDataUpdateResult(series_id, "failed", str(cache_path), str(exc)))
            continue
        results.append(
            CandidateDataUpdateResult(
                series_id=series_id,
                status="downloaded",
                cache_path=str(written_path),
                message=f"observations={len(observations)}",
            )
        )
    return _summary(series_ids, results, store, dry_run=dry_run, no_api=no_api)


def _summary(
    series_ids: list[str],
    results: list[CandidateDataUpdateResult],
    store: RawCsvStore,
    *,
    dry_run: bool,
    no_api: bool,
) -> dict:
    cached = [result.series_id for result in results if result.status == "cached"]
    downloaded = [result.series_id for result in results if result.status == "downloaded"]
    failed = [result.series_id for result in results if result.status == "failed"]
    missing = [result.series_id for result in results if result.status == "missing"]
    notes: list[str] = []
    if dry_run:
        notes.append("dry_run: no FRED API calls were made")
    if no_api:
        notes.append("no_api: local cache was checked without FRED API calls")
    if not notes:
        notes.append("candidate recession confirmation cache update")
    return {
        "required_series_count": len(series_ids),
        "already_cached_series_count": len(cached),
        "cached_series_count": len(cached),
        "downloaded_series_count": len(downloaded),
        "failed_series_count": len(failed),
        "missing_series": missing,
        "cached_series": cached,
        "downloaded_series": downloaded,
        "failed_series": failed,
        "cache_dir": str(store.root_dir / "fred"),
        "results": [result.__dict__ for result in results],
        "notes": notes,
    }
