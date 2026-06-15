from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.backtests import (
    candidate_fred_series_ids,
    load_recession_confirmation_candidate_indicators,
    update_candidate_fred_cache,
)
from business_cycle.data_sources import FredProviderError, SeriesObservation


class FakeProvider:
    def __init__(self, failing_series: set[str] | None = None) -> None:
        self.failing_series = failing_series or set()
        self.downloaded: list[str] = []

    def fetch_series_observations(self, series_id: str) -> list[SeriesObservation]:
        if series_id in self.failing_series:
            raise FredProviderError(f"failed {series_id}")
        self.downloaded.append(series_id)
        return [SeriesObservation(series_id=series_id, date="2024-01-01", value="1.0")]


def test_candidate_series_ids_are_collected_and_deduplicated(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path)
    spec = load_recession_confirmation_candidate_indicators(spec_path)

    assert candidate_fred_series_ids(spec) == ["AAA", "BAA", "CCSA"]


def test_candidate_series_ids_include_derived_formula_inputs() -> None:
    spec = load_recession_confirmation_candidate_indicators(
        "specs/backtests/recession_confirmation_candidate_indicators.yaml"
    )
    series_ids = candidate_fred_series_ids(spec)

    assert "BAA" in series_ids
    assert "AAA" in series_ids


def test_candidate_dry_run_does_not_call_provider(tmp_path: Path) -> None:
    provider = FakeProvider()
    summary = update_candidate_fred_cache(
        spec_path=write_spec(tmp_path),
        raw_dir=tmp_path / "raw",
        provider=provider,
        dry_run=True,
    )

    assert provider.downloaded == []
    assert summary["required_series_count"] == 3
    assert summary["downloaded_series_count"] == 0
    assert summary["missing_series"] == ["AAA", "BAA", "CCSA"]


def test_candidate_no_api_does_not_call_provider(tmp_path: Path) -> None:
    provider = FakeProvider()
    summary = update_candidate_fred_cache(
        spec_path=write_spec(tmp_path),
        raw_dir=tmp_path / "raw",
        provider=provider,
        no_api=True,
    )

    assert provider.downloaded == []
    assert summary["missing_series"] == ["AAA", "BAA", "CCSA"]


def test_candidate_update_downloads_missing_and_reuses_cached(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path)
    raw_dir = tmp_path / "raw"
    cached = raw_dir / "fred" / "AAA.csv"
    cached.parent.mkdir(parents=True)
    cached.write_text("series_id,date,value\nAAA,2024-01-01,1\n", encoding="utf-8")
    provider = FakeProvider()

    summary = update_candidate_fred_cache(
        spec_path=spec_path,
        raw_dir=raw_dir,
        provider=provider,
    )

    assert provider.downloaded == ["BAA", "CCSA"]
    assert summary["already_cached_series_count"] == 1
    assert summary["downloaded_series_count"] == 2


def test_candidate_update_records_failed_series(tmp_path: Path) -> None:
    provider = FakeProvider(failing_series={"BAA"})

    summary = update_candidate_fred_cache(
        spec_path=write_spec(tmp_path),
        raw_dir=tmp_path / "raw",
        provider=provider,
        force_refresh=True,
    )

    assert summary["failed_series"] == ["BAA"]
    assert summary["failed_series_count"] == 1


def test_candidate_missing_api_key_raises_without_provider(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)

    with pytest.raises(FredProviderError, match="FRED_API_KEY is not set"):
        update_candidate_fred_cache(
            spec_path=write_spec(tmp_path),
            raw_dir=tmp_path / "raw",
        )


def write_spec(tmp_path: Path) -> Path:
    path = tmp_path / "candidates.yaml"
    path.write_text(
        """
recession_confirmation_candidate_indicators:
  version: 1
  status: test
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  indicators:
    - indicator_id: credit_spread_baa_aaa
      display_name_zh: spread
      purpose_group: recession_confirmation
      provider: fred
      candidate_fred_series: [AAA, BAA, AAA]
      derived_formula: BAA - AAA
      transformation: [spread]
      proposed_score_method: credit_stress_score
      expected_phase_impact: {recession: stress}
      implementation_priority: high
    - indicator_id: continuing_jobless_claims
      display_name_zh: claims
      purpose_group: recession_confirmation
      provider: fred
      candidate_fred_series: [CCSA, AAA]
      preferred_series: CCSA
      transformation: [moving_average]
      proposed_score_method: sustained_deterioration_score
      expected_phase_impact: {recession: stress}
      implementation_priority: high
""",
        encoding="utf-8",
    )
    return path
