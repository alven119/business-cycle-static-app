from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import scripts.score_indicators as score_script


def write_catalog(path: Path) -> Path:
    path.write_text(
        """
indicators:
  - indicator_id: unemployment_rate
    provider: fred
    candidate_series:
      - provider: fred
        series_id: UNRATE
        validation_status: candidate_unverified_for_project
    score_method: level_percentile_score
    direction: lower_is_better
    parameters:
      min_periods: 3
    stale_after_days: 45
  - indicator_id: initial_jobless_claims
    provider: fred
    candidate_series:
      - provider: fred
        series_id: ICSA
        validation_status: candidate_unverified_for_project
    score_method: moving_average_slope_score
    direction: falling_is_better
    parameters:
      moving_average_window: 2
      slope_window: 3
      confirmation_window: 2
    stale_after_days: 14
""",
        encoding="utf-8",
    )
    return path


def write_catalog_with_candidate_list(path: Path) -> Path:
    path.write_text(
        """
indicators:
  - indicator_id: retail
    provider: fred
    candidate_series:
      - provider: fred
        series_id: FIRST
      - provider: fred
        series_id: SECOND
    score_method: level_percentile_score
    direction: higher_is_better
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


def test_cli_reads_local_csv_and_writes_output_json(tmp_path: Path) -> None:
    catalog_path = write_catalog(tmp_path / "catalog.yaml")
    input_dir = tmp_path / "raw"
    output_path = tmp_path / "derived" / "scores.json"
    write_raw_csv(input_dir, "UNRATE", [6, 5, 4, 3])
    write_raw_csv(input_dir, "ICSA", [10, 9, 8, 7, 6, 5])

    exit_code = score_script.main(
        [
            "--catalog-path",
            str(catalog_path),
            "--input-dir",
            str(input_dir),
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["summary"]["scored_indicators"] == 2
    assert payload["summary"]["failed_indicators"] == 0
    assert payload["results"][0]["details"]["selected_series_id"] == "ICSA"
    assert payload["results"][1]["details"]["selected_series_id"] == "UNRATE"


def test_missing_csv_becomes_failure_not_crash(tmp_path: Path) -> None:
    catalog_path = write_catalog(tmp_path / "catalog.yaml")
    output_path = tmp_path / "scores.json"

    exit_code = score_script.main(
        [
            "--catalog-path",
            str(catalog_path),
            "--input-dir",
            str(tmp_path / "missing_raw"),
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["summary"]["scored_indicators"] == 0
    assert payload["summary"]["failed_indicators"] == 2
    assert payload["failures"][0]["error_type"] == "MissingRawCsv"
    assert "indicator_id=" in payload["failures"][0]["message"]
    assert "candidate_series=" in payload["failures"][0]["message"]
    assert "expected_csv_paths=" in payload["failures"][0]["message"]


def test_indicator_id_filter_is_applied(tmp_path: Path) -> None:
    catalog_path = write_catalog(tmp_path / "catalog.yaml")
    input_dir = tmp_path / "raw"
    output_path = tmp_path / "scores.json"
    write_raw_csv(input_dir, "UNRATE", [6, 5, 4, 3])
    write_raw_csv(input_dir, "ICSA", [10, 9, 8, 7, 6, 5])

    score_script.main(
        [
            "--catalog-path",
            str(catalog_path),
            "--input-dir",
            str(input_dir),
            "--output-path",
            str(output_path),
            "--indicator-id",
            "unemployment_rate",
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_indicators"] == 1
    assert [result["indicator_id"] for result in payload["results"]] == ["unemployment_rate"]


def test_as_of_filter_is_applied(tmp_path: Path) -> None:
    catalog_path = write_catalog(tmp_path / "catalog.yaml")
    input_dir = tmp_path / "raw"
    first_output = tmp_path / "first.json"
    second_output = tmp_path / "second.json"
    write_raw_csv(input_dir, "UNRATE", [6, 5, 4, 3, 100, 200])

    common_args = [
        "--catalog-path",
        str(catalog_path),
        "--input-dir",
        str(input_dir),
        "--indicator-id",
        "unemployment_rate",
        "--as-of",
        "2020-04-01",
    ]
    score_script.main([*common_args, "--output-path", str(first_output)])
    score_script.main([*common_args, "--output-path", str(second_output)])

    first = json.loads(first_output.read_text(encoding="utf-8"))
    second = json.loads(second_output.read_text(encoding="utf-8"))
    assert second["results"][0]["score"] == first["results"][0]["score"]
    assert second["results"][0]["details"]["dispatcher"]["available_observations"] == 4


def test_first_fred_candidate_series_id() -> None:
    assert (
        score_script.first_fred_candidate_series_id(
            {
                "provider": "fred",
                "candidate_series": [{"provider": "fred", "series_id": "UNRATE"}],
            }
        )
        == "UNRATE"
    )


def test_candidate_series_list_uses_first_available_csv(tmp_path: Path) -> None:
    catalog_path = write_catalog_with_candidate_list(tmp_path / "catalog.yaml")
    input_dir = tmp_path / "raw"
    output_path = tmp_path / "scores.json"
    write_raw_csv(input_dir, "FIRST", [1, 2, 3, 4])
    write_raw_csv(input_dir, "SECOND", [10, 11, 12, 13])

    score_script.main(
        [
            "--catalog-path",
            str(catalog_path),
            "--input-dir",
            str(input_dir),
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["scored_indicators"] == 1
    assert payload["results"][0]["details"]["selected_series_id"] == "FIRST"


def test_candidate_series_list_falls_back_to_second_existing_csv(tmp_path: Path) -> None:
    catalog_path = write_catalog_with_candidate_list(tmp_path / "catalog.yaml")
    input_dir = tmp_path / "raw"
    output_path = tmp_path / "scores.json"
    write_raw_csv(input_dir, "SECOND", [10, 11, 12, 13])

    score_script.main(
        [
            "--catalog-path",
            str(catalog_path),
            "--input-dir",
            str(input_dir),
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["scored_indicators"] == 1
    assert payload["results"][0]["details"]["selected_series_id"] == "SECOND"


def test_missing_all_candidate_csv_failure_lists_candidates_and_paths(tmp_path: Path) -> None:
    catalog_path = write_catalog_with_candidate_list(tmp_path / "catalog.yaml")
    output_path = tmp_path / "scores.json"

    score_script.main(
        [
            "--catalog-path",
            str(catalog_path),
            "--input-dir",
            str(tmp_path / "raw"),
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    failure = payload["failures"][0]
    assert failure["indicator_id"] == "retail"
    assert failure["error_type"] == "MissingRawCsv"
    assert "FIRST" in failure["message"]
    assert "SECOND" in failure["message"]
    assert "expected_csv_paths=" in failure["message"]
