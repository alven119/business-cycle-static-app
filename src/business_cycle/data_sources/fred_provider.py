"""FRED data provider."""

from __future__ import annotations

import os
from typing import Any

import requests

from .base import DataProviderError, SeriesObservation


class FredProviderError(DataProviderError):
    """Raised when FRED observations cannot be downloaded or parsed."""


class FredProvider:
    """Client for the FRED series observations endpoint."""

    DEFAULT_BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def require_api_key(self) -> str:
        """Return the configured FRED API key or raise a clear error."""

        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise FredProviderError(
                "FRED_API_KEY is not set. Put it in your environment or local .env file; "
                "never commit API keys to the repository."
            )
        return api_key

    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        """Fetch observations for a FRED series."""

        clean_series_id = series_id.strip().upper()
        if not clean_series_id:
            raise FredProviderError("series_id must not be empty")

        params: dict[str, str] = {
            "series_id": clean_series_id,
            "api_key": self.require_api_key(),
            "file_type": "json",
        }
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end

        url = f"{self.base_url}/series/observations"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout_seconds)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise FredProviderError(
                f"Failed to download FRED series {clean_series_id}: {exc}"
            ) from exc
        except ValueError as exc:
            raise FredProviderError(
                f"FRED series {clean_series_id} returned invalid JSON"
            ) from exc

        if not isinstance(payload, dict):
            raise FredProviderError(f"FRED series {clean_series_id} returned unexpected payload")
        if "error_code" in payload:
            message = payload.get("error_message", "unknown FRED API error")
            raise FredProviderError(f"FRED API error for {clean_series_id}: {message}")

        raw_observations = payload.get("observations")
        if not isinstance(raw_observations, list):
            raise FredProviderError(
                f"FRED series {clean_series_id} response did not include observations"
            )

        return [
            self._parse_observation(clean_series_id, observation)
            for observation in raw_observations
        ]

    @staticmethod
    def _parse_observation(series_id: str, observation: Any) -> SeriesObservation:
        if not isinstance(observation, dict):
            raise FredProviderError(f"FRED series {series_id} included a non-object observation")

        date = observation.get("date")
        value = observation.get("value")
        if not isinstance(date, str) or not isinstance(value, str):
            raise FredProviderError(
                f"FRED series {series_id} observation is missing string date/value fields"
            )

        return SeriesObservation(
            series_id=series_id,
            date=date,
            value=value,
            realtime_start=_optional_str(observation.get("realtime_start")),
            realtime_end=_optional_str(observation.get("realtime_end")),
        )


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None
