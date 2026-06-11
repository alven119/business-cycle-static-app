"""Base interfaces for macroeconomic data providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class DataProviderError(RuntimeError):
    """Raised when a data provider cannot return requested data."""


@dataclass(frozen=True)
class SeriesObservation:
    """One raw time-series observation from a data provider."""

    series_id: str
    date: str
    value: str
    realtime_start: str | None = None
    realtime_end: str | None = None


class DataProvider(Protocol):
    """Protocol implemented by raw data providers."""

    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        """Fetch raw observations for one provider series."""

