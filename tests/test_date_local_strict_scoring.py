from __future__ import annotations

import json
from pathlib import Path

import scripts.score_indicators as score_script
from business_cycle.audits.point_in_time_coverage import discover_formal_dependencies
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def _write_rows(cache: PointInTimeCache, series_id: str, *, start_year: int) -> None:
    rows = []
    for year in range(start_year, 2010):
        for month in range(1, 13):
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": f"{year}-{month:02d}-01",
                    "value": str(100 + month),
                    "realtime_start": f"{year}-{month:02d}-15",
                    "realtime_end": "9999-12-31",
                }
            )
    cache.write_series(
        series_id,
        rows,
        query_mode="vintage_as_of",
        observation_start=f"{start_year}-01-01",
        observation_end="2009-12-31",
        as_of_start=f"{start_year}-01-01",
        as_of_end="2009-12-31",
    )


def test_strict_scoring_uses_date_local_readiness(tmp_path: Path) -> None:
    deps = discover_formal_dependencies("specs/indicator_catalog.yaml")
    cache = PointInTimeCache(tmp_path / "cache")
    for series_id in deps.direct_series_ids:
        _write_rows(cache, series_id, start_year=2005 if series_id == "DGS10" else 1998)

    output_2008 = tmp_path / "scores_2008.json"
    score_script.main(
        [
            "--as-of",
            "2008-09-30",
            "--data-mode",
            "vintage_as_of",
            "--point-in-time-cache-dir",
            str(tmp_path / "cache"),
            "--output",
            str(output_2008),
        ]
    )
    summary_2008 = json.loads(output_2008.read_text(encoding="utf-8"))["summary"]
    assert summary_2008["scored_indicators"] == 13
    assert "DGS10" not in summary_2008["missing_series"]

    output_2000 = tmp_path / "scores_2000.json"
    score_script.main(
        [
            "--as-of",
            "2000-03-31",
            "--data-mode",
            "vintage_as_of",
            "--point-in-time-cache-dir",
            str(tmp_path / "cache"),
            "--output",
            str(output_2000),
        ]
    )
    summary_2000 = json.loads(output_2000.read_text(encoding="utf-8"))["summary"]
    assert summary_2000["scored_indicators"] < 13
    assert "DGS10" in summary_2000["missing_series"]
    assert summary_2000["revised_fallback_series"] == []
