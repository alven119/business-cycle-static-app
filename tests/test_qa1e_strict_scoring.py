import json

import scripts.score_indicators as score_script
from business_cycle.indicators.catalog import load_indicator_catalog


def test_revised_scoring_default_still_unchanged(tmp_path) -> None:
    input_dir = tmp_path / "fred"
    input_dir.mkdir()
    _seed_revised_indicator_fixtures(input_dir)
    output = tmp_path / "scores.json"

    score_script.main(
        [
            "--as-of",
            "2019-12-31",
            "--input-dir",
            str(input_dir),
            "--output",
            str(output),
        ]
    )

    summary = json.loads(output.read_text(encoding="utf-8"))["summary"]
    assert summary["requested_data_mode"] == "revised"
    assert summary["actual_data_mode"] == "revised"
    assert summary["scored_indicators"] == 13


def _seed_revised_indicator_fixtures(input_dir) -> None:
    series_ids: set[str] = set()
    for entry in load_indicator_catalog("specs/indicator_catalog.yaml"):
        series_ids.update(score_script.fred_candidate_series_ids(entry))
    rows = ["series_id,date,value,realtime_start,realtime_end"]
    dates = [f"{year}-{month:02d}-28" for year in range(2010, 2020) for month in range(1, 13)]
    for index, series_id in enumerate(sorted(series_ids), start=1):
        series_rows = [
            f"{series_id},{date},{100 + index + offset * 0.5:.2f},2020-01-01,2020-01-01"
            for offset, date in enumerate(dates)
        ]
        (input_dir / f"{series_id}.csv").write_text(
            "\n".join([rows[0], *series_rows]) + "\n",
            encoding="utf-8",
        )
