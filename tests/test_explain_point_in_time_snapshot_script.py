from __future__ import annotations

from pathlib import Path

import scripts.explain_point_in_time_snapshot as explain
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_explain_snapshot_reports_date_local_readiness(tmp_path: Path, capsys) -> None:
    cache = PointInTimeCache(tmp_path / "cache")
    cache.write_series(
        "DGS10",
        [
            {
                "series_id": "DGS10",
                "observation_date": "2008-09-29",
                "value": "3.85",
                "realtime_start": "2008-09-30",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start="2008-01-01",
        observation_end="2008-12-31",
        as_of_start="2008-01-01",
        as_of_end="2008-12-31",
    )

    explain.main(
        [
            "--series-id",
            "DGS10",
            "--as-of",
            "2008-09-30",
            "--cache-dir",
            str(tmp_path / "cache"),
        ]
    )

    output = capsys.readouterr().out
    assert "snapshot_as_of_ready=true" in output
    assert "full_required_horizon_ready=false" in output
    assert "selected_observation_date=2008-09-29" in output


def test_explain_snapshot_reports_pre_coverage_missing(tmp_path: Path, capsys) -> None:
    cache = PointInTimeCache(tmp_path / "cache")
    cache.write_series(
        "DGS10",
        [
            {
                "series_id": "DGS10",
                "observation_date": "2008-09-29",
                "value": "3.85",
                "realtime_start": "2008-09-30",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start="2008-01-01",
        observation_end="2008-12-31",
        as_of_start="2008-01-01",
        as_of_end="2008-12-31",
    )

    explain.main(
        [
            "--series-id",
            "DGS10",
            "--as-of",
            "2000-03-31",
            "--cache-dir",
            str(tmp_path / "cache"),
        ]
    )

    output = capsys.readouterr().out
    assert "snapshot_as_of_ready=false" in output
    assert "missing_reason=history_before_exact_vintage_coverage" in output
