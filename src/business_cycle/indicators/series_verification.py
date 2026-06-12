"""Verify candidate data series from the indicator catalog."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from business_cycle.data_sources.base import DataProvider, DataProviderError


@dataclass(frozen=True)
class SeriesVerificationResult:
    """Result of verifying one catalog candidate series."""

    indicator_id: str
    series_id: str
    provider: str
    status: str
    observations_count: int
    first_date: str | None
    last_date: str | None
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def verify_catalog_series(
    catalog_entries: list[dict[str, Any]],
    provider_map: dict[str, DataProvider],
) -> list[SeriesVerificationResult]:
    """Verify candidate series for catalog entries using provider instances."""

    results: list[SeriesVerificationResult] = []
    for entry in catalog_entries:
        indicator_id = str(entry.get("indicator_id", ""))
        candidates = _candidate_series(entry)
        if not candidates:
            results.append(
                SeriesVerificationResult(
                    indicator_id=indicator_id,
                    series_id="",
                    provider=str(entry.get("provider", "")),
                    status="missing_candidate_series",
                    observations_count=0,
                    first_date=None,
                    last_date=None,
                    message="No candidate_series configured for this indicator.",
                )
            )
            continue

        for candidate in candidates:
            provider_name = candidate["provider"]
            series_id = candidate["series_id"]
            if provider_name != "fred" or provider_name not in provider_map:
                results.append(
                    SeriesVerificationResult(
                        indicator_id=indicator_id,
                        series_id=series_id,
                        provider=provider_name,
                        status="provider_not_supported",
                        observations_count=0,
                        first_date=None,
                        last_date=None,
                        message=f"Provider {provider_name!r} is not supported by this verifier.",
                    )
                )
                continue

            provider = provider_map[provider_name]
            results.append(_verify_one_series(indicator_id, provider_name, series_id, provider))

    return results


def _verify_one_series(
    indicator_id: str,
    provider_name: str,
    series_id: str,
    provider: DataProvider,
) -> SeriesVerificationResult:
    try:
        observations = provider.fetch_series_observations(series_id)
    except DataProviderError as exc:
        return SeriesVerificationResult(
            indicator_id=indicator_id,
            series_id=series_id,
            provider=provider_name,
            status="download_failed",
            observations_count=0,
            first_date=None,
            last_date=None,
            message=str(exc),
        )

    if not observations:
        return SeriesVerificationResult(
            indicator_id=indicator_id,
            series_id=series_id,
            provider=provider_name,
            status="empty_observations",
            observations_count=0,
            first_date=None,
            last_date=None,
            message="Provider returned no observations.",
        )

    sorted_observations = sorted(observations, key=lambda observation: observation.date)
    return SeriesVerificationResult(
        indicator_id=indicator_id,
        series_id=series_id,
        provider=provider_name,
        status="ok",
        observations_count=len(sorted_observations),
        first_date=sorted_observations[0].date,
        last_date=sorted_observations[-1].date,
        message="Series downloaded successfully.",
    )


def _candidate_series(entry: dict[str, Any]) -> list[dict[str, str]]:
    raw_candidates = entry.get("candidate_series")
    if raw_candidates is None:
        return []
    if isinstance(raw_candidates, (str, dict)):
        raw_items = [raw_candidates]
    elif isinstance(raw_candidates, list):
        raw_items = raw_candidates
    else:
        return []

    candidates: list[dict[str, str]] = []
    for raw_item in raw_items:
        candidate = _normalize_candidate(raw_item, default_provider=str(entry.get("provider", "fred")))
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _normalize_candidate(raw_item: Any, *, default_provider: str) -> dict[str, str] | None:
    if isinstance(raw_item, str):
        return {"provider": default_provider, "series_id": raw_item.strip().upper()}
    if not isinstance(raw_item, dict):
        return None

    series_id = raw_item.get("series_id") or raw_item.get("id")
    if not isinstance(series_id, str) or not series_id.strip():
        return None
    provider = raw_item.get("provider", default_provider)
    if not isinstance(provider, str) or not provider.strip():
        provider = default_provider
    return {"provider": provider.strip().lower(), "series_id": series_id.strip().upper()}
