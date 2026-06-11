from __future__ import annotations

from pathlib import Path

import pytest
import requests

import scripts.update_data as update_data
from business_cycle.data_sources.base import SeriesObservation
from business_cycle.data_sources.fred_provider import FredProvider, FredProviderError
from business_cycle.storage.raw_store import RawCsvStore
from scripts.update_data import main, series_ids_from_catalog


class FakeResponse:
    def __init__(self, payload: object, status_error: Exception | None = None) -> None:
        self.payload = payload
        self.status_error = status_error

    def raise_for_status(self) -> None:
        if self.status_error:
            raise self.status_error

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def get(self, url: str, *, params: dict[str, str], timeout: float) -> FakeResponse:
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return self.response


def test_fred_provider_reads_api_key_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRED_API_KEY", "test-key")
    session = FakeSession(
        FakeResponse(
            {
                "observations": [
                    {
                        "realtime_start": "2024-01-01",
                        "realtime_end": "2024-01-01",
                        "date": "2024-01-01",
                        "value": "1.23",
                    }
                ]
            }
        )
    )

    provider = FredProvider(session=session)  # type: ignore[arg-type]
    observations = provider.fetch_series_observations(
        "unrate",
        observation_start="2020-01-01",
        observation_end="2020-12-31",
    )

    assert observations[0].series_id == "UNRATE"
    assert observations[0].date == "2024-01-01"
    assert observations[0].value == "1.23"
    assert session.calls[0]["params"] == {
        "series_id": "UNRATE",
        "api_key": "test-key",
        "file_type": "json",
        "observation_start": "2020-01-01",
        "observation_end": "2020-12-31",
    }


def test_fred_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    provider = FredProvider(api_key="")

    with pytest.raises(FredProviderError, match="FRED_API_KEY is not set"):
        provider.fetch_series_observations("UNRATE")


def test_fred_provider_raises_clear_error_on_http_failure() -> None:
    session = FakeSession(
        FakeResponse(
            {},
            status_error=requests.HTTPError("500 Server Error"),
        )
    )
    provider = FredProvider(api_key="test-key", session=session)  # type: ignore[arg-type]

    with pytest.raises(FredProviderError, match="Failed to download FRED series UNRATE"):
        provider.fetch_series_observations("UNRATE")


def test_fred_provider_raises_clear_error_on_api_error_payload() -> None:
    session = FakeSession(
        FakeResponse({"error_code": 400, "error_message": "Bad request"})
    )
    provider = FredProvider(api_key="test-key", session=session)  # type: ignore[arg-type]

    with pytest.raises(FredProviderError, match="FRED API error for UNRATE: Bad request"):
        provider.fetch_series_observations("UNRATE")


def test_raw_csv_store_round_trips_observations(tmp_path: Path) -> None:
    provider = FredProvider(
        api_key="test-key",
        session=FakeSession(
            FakeResponse({"observations": [{"date": "2024-01-01", "value": "."}]})
        ),  # type: ignore[arg-type]
    )
    observations = provider.fetch_series_observations("UNRATE")

    store = RawCsvStore(tmp_path)
    path = store.write_observations("fred", "UNRATE", observations)

    assert path == tmp_path / "fred" / "UNRATE.csv"
    assert store.exists("fred", "UNRATE")
    assert store.read_observations("fred", "UNRATE") == observations


def test_series_ids_from_catalog_uses_unique_fred_source_priority(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text(
        """
indicators:
  - provider: fred
    source_priority:
      - fred: UNRATE
      - fred: ICSA
  - provider: fred
    source_priority:
      - fred: UNRATE
  - provider: other
    source_priority:
      - fred: SHOULD_NOT_USE
""",
        encoding="utf-8",
    )

    assert series_ids_from_catalog(catalog_path) == ["UNRATE", "ICSA"]


def test_update_data_dry_run_does_not_require_api_key(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text(
        """
indicators:
  - provider: fred
    source_priority:
      - fred: UNRATE
""",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--catalog",
            str(catalog_path),
            "--raw-dir",
            str(tmp_path / "raw"),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert "dry-run fred series=UNRATE cache=not_cached" in capsys.readouterr().out


def test_update_data_skips_cache_unless_force_refresh(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text(
        """
indicators:
  - provider: fred
    source_priority:
      - fred: UNRATE
""",
        encoding="utf-8",
    )
    raw_dir = tmp_path / "raw"
    store = RawCsvStore(raw_dir)
    store.write_observations(
        "fred",
        "UNRATE",
        [SeriesObservation(series_id="UNRATE", date="2024-01-01", value="1.0")],
    )

    calls: list[str] = []

    class FakeProvider:
        def fetch_series_observations(
            self,
            series_id: str,
            *,
            observation_start: str | None = None,
            observation_end: str | None = None,
        ) -> list[SeriesObservation]:
            calls.append(series_id)
            return [SeriesObservation(series_id=series_id, date="2024-02-01", value="2.0")]

    monkeypatch.setattr(update_data, "FredProvider", FakeProvider)

    assert main(["--catalog", str(catalog_path), "--raw-dir", str(raw_dir)]) == 0
    assert calls == []
    assert store.read_observations("fred", "UNRATE")[0].value == "1.0"

    assert (
        main(["--catalog", str(catalog_path), "--raw-dir", str(raw_dir), "--force-refresh"])
        == 0
    )
    assert calls == ["UNRATE"]
    assert store.read_observations("fred", "UNRATE")[0].value == "2.0"
