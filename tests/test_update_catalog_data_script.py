from __future__ import annotations

from pathlib import Path

import pytest

import scripts.update_catalog_data as update_catalog_data
from business_cycle.data_sources import FredProviderError, SeriesObservation
from business_cycle.storage.raw_store import RawCsvStore


class FakeProvider:
    def __init__(self, failing_series: set[str] | None = None) -> None:
        self.failing_series = failing_series or set()
        self.downloaded: list[str] = []

    def fetch_series_observations(self, series_id: str) -> list[SeriesObservation]:
        if series_id in self.failing_series:
            raise FredProviderError(f"failed {series_id}")
        self.downloaded.append(series_id)
        return [SeriesObservation(series_id=series_id, date="2024-01-01", value="1.0")]


def catalog_entries() -> list[dict]:
    return [
        {
            "indicator_id": "labor",
            "provider": "fred",
            "candidate_series": [
                {"provider": "fred", "series_id": "AAA"},
                {"provider": "fred", "series_id": "BBB"},
            ],
        },
        {
            "indicator_id": "consumer",
            "provider": "fred",
            "candidate_series": {"provider": "fred", "series_id": "CCC"},
        },
        {
            "indicator_id": "missing",
            "provider": "fred",
        },
    ]


def test_catalog_fred_candidates_expands_candidate_series_list() -> None:
    candidates = update_catalog_data.catalog_fred_candidates(catalog_entries())

    assert [(candidate.indicator_id, candidate.series_id) for candidate in candidates[:2]] == [
        ("labor", "AAA"),
        ("labor", "BBB"),
    ]


def test_indicator_id_filter_is_applied() -> None:
    candidates = update_catalog_data.catalog_fred_candidates(
        catalog_entries(),
        indicator_ids=["consumer"],
    )

    assert [(candidate.indicator_id, candidate.series_id) for candidate in candidates] == [
        ("consumer", "CCC")
    ]


def test_series_id_filter_is_applied() -> None:
    candidates = update_catalog_data.catalog_fred_candidates(
        catalog_entries(),
        series_ids=["bbb"],
    )

    assert [(candidate.indicator_id, candidate.series_id) for candidate in candidates] == [
        ("labor", "BBB")
    ]


def test_dry_run_does_not_download(tmp_path: Path) -> None:
    candidates = update_catalog_data.catalog_fred_candidates(catalog_entries(), indicator_ids=["labor"])
    results = update_catalog_data.dry_run_results(candidates, store=RawCsvStore(tmp_path))

    assert {result.status for result in results} == {"skipped"}
    assert update_catalog_data.summary_counts(results) == {
        "total_series": 2,
        "updated_series": 0,
        "failed_series": 0,
        "skipped_series": 2,
    }


def test_single_failure_does_not_stop_other_series(tmp_path: Path) -> None:
    candidates = update_catalog_data.catalog_fred_candidates(catalog_entries(), indicator_ids=["labor"])
    provider = FakeProvider(failing_series={"AAA"})

    results = update_catalog_data.update_catalog_series(
        candidates,
        provider=provider,  # type: ignore[arg-type]
        store=RawCsvStore(tmp_path),
        force_refresh=True,
    )

    assert [result.status for result in results] == ["failed", "updated"]
    assert provider.downloaded == ["BBB"]
    assert update_catalog_data.summary_counts(results) == {
        "total_series": 2,
        "updated_series": 1,
        "failed_series": 1,
        "skipped_series": 0,
    }


def test_missing_candidate_series_is_skipped() -> None:
    candidates = update_catalog_data.catalog_fred_candidates(catalog_entries(), indicator_ids=["missing"])

    assert candidates[0].status == "skipped"
    assert candidates[0].series_id is None


def test_missing_fred_api_key_exits_with_clear_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text(
        """
indicators:
  - indicator_id: labor
    provider: fred
    candidate_series:
      - provider: fred
        series_id: AAA
""",
        encoding="utf-8",
    )
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    monkeypatch.setattr(update_catalog_data, "load_dotenv", lambda: None)

    with pytest.raises(SystemExit) as exc_info:
        update_catalog_data.main(["--catalog-path", str(catalog_path), "--raw-dir", str(tmp_path)])

    assert exc_info.value.code == 1
    assert "FRED_API_KEY is not set" in capsys.readouterr().err
