from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
    write_current_data_refresh_manifest,
)
from business_cycle.data_sources import FredProviderError, SeriesObservation


class FakeProvider:
    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        return [
            SeriesObservation(series_id=series_id, date="2026-05-31", value="1.0"),
            SeriesObservation(series_id=series_id, date="2026-06-15", value="2.0"),
        ]


class FailingProvider:
    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        raise FredProviderError("api_key=secret-token failed")


def test_refresh_without_key_falls_back_to_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    manifest = build_current_data_refresh_manifest(allow_fixture_fallback=True)

    assert manifest["live_fetch_attempted"] is False
    assert manifest["live_fetch_succeeded"] is False
    assert manifest["live_fetch_skipped_reason"] == "missing_fred_api_key"
    assert manifest["fixture_used"] is True
    assert manifest["fixture_mislabeled_as_live_count"] == 0
    assert manifest["secret_logged_count"] == 0


def test_no_live_fetch_is_hermetic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret-token")
    manifest = build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )

    assert manifest["live_fetch_attempted"] is False
    assert manifest["live_fetch_skipped_reason"] == "live_fetch_disabled_by_cli"
    assert manifest["fetched_series_count"] == 0
    assert manifest["stale_series_count_after"] == manifest["stale_series_count_before"]


def test_mock_live_provider_writes_tmp_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret-token")
    manifest = build_current_data_refresh_manifest(
        cache_dir=tmp_path / "cache",
        provider=FakeProvider(),
    )

    assert manifest["live_fetch_attempted"] is True
    assert manifest["live_fetch_succeeded"] is True
    assert manifest["fetched_series_count"] > 0
    assert manifest["cache_write_attempted"] is True
    assert manifest["cache_write_succeeded"] is True
    assert manifest["cache_dir_kind"] == "tmp"
    assert manifest["raw_data_committed"] is False
    assert manifest["secret_logged"] is False


def test_provider_error_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret-token")
    manifest = build_current_data_refresh_manifest(provider=FailingProvider())

    assert manifest["live_fetch_attempted"] is True
    assert manifest["live_fetch_succeeded"] is False
    assert manifest["provider_error_class"] == "FredProviderError"
    assert "secret-token" not in str(manifest["provider_error_message_redacted"])
    assert manifest["network_error_fails_closed"] is True


def test_manifest_output_must_stay_under_tmp(tmp_path: Path) -> None:
    manifest = build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )
    result = write_current_data_refresh_manifest(
        manifest,
        output=tmp_path / "manifest.json",
    )

    assert result["refresh_manifest_artifact_count"] == 1
    assert result["forbidden_repo_output_count"] == 0
    with pytest.raises(ValueError):
        write_current_data_refresh_manifest(
            manifest,
            output=Path("data/backtests/manifest.json"),
        )
