"""ALFRED/FRED vintage observation provider."""

from __future__ import annotations

import time
import re
from dataclasses import dataclass
from typing import Any

import requests

from business_cycle.data_sources.fred_provider import FredProvider, FredProviderError


class AlfredProviderError(FredProviderError):
    """Raised when ALFRED vintage observations cannot be fetched or parsed."""


@dataclass(frozen=True)
class AlfredObservation:
    """One ALFRED observation row with real-time period metadata."""

    series_id: str
    observation_date: str
    value: str
    realtime_start: str
    realtime_end: str


class AlfredProvider(FredProvider):
    """Client for FRED/ALFRED series observations and vintage date endpoints."""

    def __init__(
        self,
        *,
        base_url: str = FredProvider.DEFAULT_BASE_URL,
        timeout_seconds: float = 30.0,
        session: requests.Session | None = None,
        max_retries: int = 2,
        retry_sleep_seconds: float = 0.2,
        page_limit: int = 100000,
    ) -> None:
        super().__init__(base_url=base_url, timeout_seconds=timeout_seconds, session=session)
        self.max_retries = max_retries
        self.retry_sleep_seconds = retry_sleep_seconds
        self.page_limit = page_limit
        self.last_request_count = 0
        self.last_pagination_count = 0
        self.retry_count = 0
        self.rate_limit_retry_count = 0
        self.last_http_status: int | None = None
        self.last_response_content_type: str | None = None
        self.last_response_byte_count = 0
        self.last_error_class: str | None = None
        self.last_error_message_redacted: str | None = None

    def fetch_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
        realtime_start: str | None = None,
        realtime_end: str | None = None,
        output_type: int = 1,
    ) -> list[AlfredObservation]:
        """Fetch raw units=lin observations with ALFRED real-time metadata."""

        clean_series_id = series_id.strip().upper()
        if not clean_series_id:
            raise AlfredProviderError("series_id must not be empty")
        if output_type not in {1, 4}:
            raise AlfredProviderError("Only output_type=1 and output_type=4 are supported")

        params: dict[str, str] = {
            "series_id": clean_series_id,
            "api_key": self.require_api_key(),
            "file_type": "json",
            "units": "lin",
            "output_type": str(output_type),
            "limit": str(self.page_limit),
            "offset": "0",
        }
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        observations: list[AlfredObservation] = []
        self.last_request_count = 0
        self.last_pagination_count = 0
        self.retry_count = 0
        self.rate_limit_retry_count = 0
        self.last_http_status = None
        self.last_response_content_type = None
        self.last_response_byte_count = 0
        self.last_error_class = None
        self.last_error_message_redacted = None
        while True:
            payload = self._get_json("series/observations", params, clean_series_id)
            self.last_request_count += 1
            raw_observations = payload.get("observations")
            if not isinstance(raw_observations, list):
                raise AlfredProviderError(
                    f"FRED series {clean_series_id} response did not include observations"
                )
            observations.extend(
                self._parse_alfred_observation(clean_series_id, row)
                for row in raw_observations
            )
            count = int(payload.get("count", len(raw_observations)))
            limit = int(payload.get("limit", params["limit"]))
            offset = int(payload.get("offset", params["offset"]))
            next_offset = offset + limit
            if next_offset >= count or not raw_observations:
                break
            params["offset"] = str(next_offset)
            self.last_pagination_count += 1
        return observations

    def fetch_vintage_dates(
        self,
        series_id: str,
        *,
        realtime_start: str | None = None,
        realtime_end: str | None = None,
    ) -> list[str]:
        """Fetch vintage date list for diagnostics, not as a release calendar."""

        clean_series_id = series_id.strip().upper()
        params: dict[str, str] = {
            "series_id": clean_series_id,
            "api_key": self.require_api_key(),
            "file_type": "json",
        }
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end
        payload = self._get_json("series/vintagedates", params, clean_series_id)
        dates = payload.get("vintage_dates")
        if not isinstance(dates, list) or not all(isinstance(item, str) for item in dates):
            raise AlfredProviderError(f"FRED series {clean_series_id} returned invalid vintage_dates")
        return dates

    def _get_json(self, endpoint: str, params: dict[str, str], series_id: str) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        safe_params = {key: value for key, value in params.items() if key != "api_key"}
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout_seconds)
                self.last_http_status = getattr(response, "status_code", None)
                headers = getattr(response, "headers", {}) or {}
                self.last_response_content_type = headers.get("Content-Type")
                content = getattr(response, "content", None)
                if isinstance(content, bytes):
                    self.last_response_byte_count = len(content)
                else:
                    text = getattr(response, "text", "")
                    self.last_response_byte_count = len(str(text).encode("utf-8"))
                if getattr(response, "status_code", None) == 429:
                    retry_after = response.headers.get("Retry-After") if hasattr(response, "headers") else None
                    raise requests.HTTPError(
                        f"rate limited; retry_after={retry_after or 'unspecified'}",
                        response=response,
                    )
                response.raise_for_status()
                payload = response.json()
            except requests.Timeout as exc:
                last_error = exc
                self.last_error_class = type(exc).__name__
                self.last_error_message_redacted = _redact(str(exc))
            except requests.RequestException as exc:
                last_error = exc
                self.last_error_class = type(exc).__name__
                self.last_error_message_redacted = _redact(str(exc))
            except ValueError as exc:
                self.last_error_class = type(exc).__name__
                self.last_error_message_redacted = "invalid JSON"
                raise AlfredProviderError(f"FRED series {series_id} returned invalid JSON") from exc
            else:
                if not isinstance(payload, dict):
                    raise AlfredProviderError(f"FRED series {series_id} returned unexpected payload")
                if "error_code" in payload:
                    message = payload.get("error_message", "unknown FRED API error")
                    raise AlfredProviderError(f"FRED API error for {series_id}: {message}")
                return payload
            if attempt < self.max_retries:
                self.retry_count += 1
                sleep_seconds = self.retry_sleep_seconds
                response = getattr(last_error, "response", None)
                retry_after = getattr(response, "headers", {}).get("Retry-After") if response else None
                if retry_after:
                    self.rate_limit_retry_count += 1
                    try:
                        sleep_seconds = min(float(retry_after), 5.0)
                    except ValueError:
                        sleep_seconds = self.retry_sleep_seconds
                time.sleep(sleep_seconds)
        raise AlfredProviderError(
            "Failed to download FRED series "
            f"{series_id} endpoint={endpoint} params={safe_params} "
            f"http_status={self.last_http_status} "
            f"content_type={self.last_response_content_type} "
            f"byte_count={self.last_response_byte_count} "
            f"error_class={self.last_error_class} "
            f"error_message={self.last_error_message_redacted}"
        ) from last_error

    @staticmethod
    def _parse_alfred_observation(series_id: str, row: Any) -> AlfredObservation:
        if not isinstance(row, dict):
            raise AlfredProviderError(f"FRED series {series_id} included a non-object observation")
        required = ("date", "value", "realtime_start", "realtime_end")
        missing = [field for field in required if not isinstance(row.get(field), str)]
        if missing:
            raise AlfredProviderError(
                f"FRED series {series_id} observation missing fields: {', '.join(missing)}"
            )
        return AlfredObservation(
            series_id=series_id,
            observation_date=str(row["date"]),
            value=str(row["value"]),
            realtime_start=str(row["realtime_start"]),
            realtime_end=str(row["realtime_end"]),
        )


def _redact(message: str) -> str:
    text = message.replace("FRED_API_KEY", "redacted_key")
    text = re.sub(r"(?i)(api_key|redacted_key)=([^&\\s)\"']+)", r"\1=[REDACTED]", text)
    return text.replace("api_key", "redacted_key")
