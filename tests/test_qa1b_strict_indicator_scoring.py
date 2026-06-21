from __future__ import annotations

import json
from pathlib import Path

import scripts.score_indicators as score_script
from business_cycle.audits.point_in_time_coverage import discover_formal_dependencies
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_strict_indicator_scoring_scores_all_formal_indicators(tmp_path: Path) -> None:
    deps = discover_formal_dependencies("specs/indicator_catalog.yaml")
    cache = PointInTimeCache(tmp_path / "cache")
    for series_id in deps.direct_series_ids:
        rows = []
        for year in range(1998, 2009):
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
            observation_start="1998-01-01",
            observation_end="2008-12-31",
            as_of_start="1776-07-04",
            as_of_end="2008-12-31",
        )

    output = tmp_path / "scores.json"
    score_script.main(
        [
            "--as-of",
            "2008-09-30",
            "--data-mode",
            "vintage_as_of",
            "--point-in-time-cache-dir",
            str(tmp_path / "cache"),
            "--output",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"]["total_indicators"] == 13
    assert payload["summary"]["scored_indicators"] == 13
    assert payload["summary"]["failed_indicators"] == 0
    assert payload["summary"]["requested_data_mode"] == "vintage_as_of"
    assert payload["summary"]["actual_data_mode"] == "vintage_as_of"
    assert payload["summary"]["point_in_time"] is True
    assert payload["summary"]["proxy_series"] == []
    assert payload["summary"]["revised_fallback_series"] == []
    assert payload["summary"]["missing_series"] == []
    assert payload["summary"]["vintage_as_of"] == "2008-09-30"


def test_strict_point_in_time_alias_blocks_missing_cache(tmp_path: Path) -> None:
    output = tmp_path / "scores.json"

    score_script.main(
        [
            "--as-of",
            "2008-09-30",
            "--data-mode",
            "strict_point_in_time",
            "--point-in-time-cache-dir",
            str(tmp_path / "cache"),
            "--output",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"]["requested_data_mode"] == "strict_point_in_time"
    assert payload["summary"]["actual_data_mode"] == "blocked"
    assert payload["summary"]["point_in_time"] is False
    assert payload["summary"]["revised_fallback_series"] == []
