from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import scripts.score_indicators as score_script
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def write_catalog(path: Path) -> Path:
    path.write_text(
        """
indicators:
  - indicator_id: unemployment_rate
    provider: fred
    candidate_series:
      - provider: fred
        series_id: UNRATE
    score_method: level_percentile_score
    direction: lower_is_better
    parameters:
      min_periods: 3
    stale_after_days: 45
""",
        encoding="utf-8",
    )
    return path


def write_raw_csv(input_dir: Path, series_id: str, values: list[float | int]) -> Path:
    input_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(
        {
            "series_id": series_id,
            "date": pd.date_range("2020-01-01", periods=len(values), freq="MS"),
            "value": values,
        }
    )
    path = input_dir / f"{series_id}.csv"
    frame.to_csv(path, index=False)
    return path


def test_strict_scoring_blocks_missing_vintage_without_revised_fallback(tmp_path: Path) -> None:
    catalog_path = write_catalog(tmp_path / "catalog.yaml")
    revised_dir = tmp_path / "revised"
    output_path = tmp_path / "scores.json"
    write_raw_csv(revised_dir, "UNRATE", [1, 2, 3, 4])

    score_script.main(
        [
            "--catalog-path",
            str(catalog_path),
            "--input-dir",
            str(revised_dir),
            "--output",
            str(output_path),
            "--indicator-id",
            "unemployment_rate",
            "--as-of",
            "2020-04-30",
            "--data-mode",
            "vintage_as_of",
            "--point-in-time-cache-dir",
            str(tmp_path / "missing_cache"),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["scored_indicators"] == 0
    assert payload["summary"]["actual_data_mode"] == "blocked"
    assert payload["summary"]["point_in_time"] is False


def test_production_default_revised_path_still_scores(tmp_path: Path) -> None:
    catalog_path = write_catalog(tmp_path / "catalog.yaml")
    input_dir = tmp_path / "raw"
    output_path = tmp_path / "scores.json"
    write_raw_csv(input_dir, "UNRATE", [6, 5, 4, 3])

    score_script.main(
        [
            "--catalog-path",
            str(catalog_path),
            "--input-dir",
            str(input_dir),
            "--output",
            str(output_path),
            "--indicator-id",
            "unemployment_rate",
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["requested_data_mode"] == "revised"
    assert payload["summary"]["scored_indicators"] == 1


def test_strict_scoring_uses_cache_when_available(tmp_path: Path) -> None:
    catalog_path = write_catalog(tmp_path / "catalog.yaml")
    cache_dir = tmp_path / "cache"
    output_path = tmp_path / "scores.json"
    rows = []
    for index, value in enumerate([6, 5, 4, 3], start=1):
        rows.append(
            {
                "series_id": "UNRATE",
                "observation_date": pd.Timestamp(2020, index, 1).date().isoformat(),
                "value": str(value),
                "realtime_start": pd.Timestamp(2020, index, 15).date().isoformat(),
                "realtime_end": "9999-12-31",
            }
        )
    PointInTimeCache(cache_dir).write_series(
        "UNRATE",
        rows,
        query_mode="vintage_as_of",
        observation_start=None,
        observation_end=None,
        as_of_start=None,
        as_of_end=None,
    )

    score_script.main(
        [
            "--catalog-path",
            str(catalog_path),
            "--output",
            str(output_path),
            "--indicator-id",
            "unemployment_rate",
            "--as-of",
            "2020-04-30",
            "--data-mode",
            "vintage_as_of",
            "--point-in-time-cache-dir",
            str(cache_dir),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["point_in_time"] is True
    assert payload["summary"]["scored_indicators"] == 1
