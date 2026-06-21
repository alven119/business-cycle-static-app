from __future__ import annotations

from pathlib import Path

import pandas as pd

import scripts.compare_revised_vs_point_in_time as compare
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_compare_revised_vs_point_in_time_reports_no_silent_fallback(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    revised_dir = tmp_path / "revised"
    revised_dir.mkdir()
    pd.DataFrame(
        {"series_id": ["UNRATE"], "date": ["2020-01-31"], "value": [2.0]}
    ).to_csv(revised_dir / "UNRATE.csv", index=False)
    PointInTimeCache(cache_dir).write_series(
        "UNRATE",
        [
            {
                "series_id": "UNRATE",
                "observation_date": "2020-01-31",
                "value": "1.0",
                "realtime_start": "2020-02-15",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start=None,
        observation_end=None,
        as_of_start=None,
        as_of_end=None,
    )

    exit_code = compare.main(
        [
            "--series-id",
            "UNRATE",
            "--scenario-id",
            "global_financial_crisis",
            "--max-periods",
            "1",
            "--cache-dir",
            str(cache_dir),
            "--revised-dir",
            str(revised_dir),
        ]
    )

    assert exit_code == 0
