from __future__ import annotations

from pathlib import Path

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
    score_method: level_percentile_score
    direction: lower_is_better
    parameters:
      min_periods: 3
    stale_after_days: 45
""",
        encoding="utf-8",
    )
    return path


def test_strict_scoring_still_blocks_missing_cache_without_fallback(tmp_path: Path) -> None:
    catalog = write_catalog(tmp_path / "catalog.yaml")
    output = tmp_path / "scores.json"

    score_script.main(
        [
            "--catalog-path",
            str(catalog),
            "--output",
            str(output),
            "--as-of",
            "2020-03-31",
            "--data-mode",
            "vintage_as_of",
            "--point-in-time-cache-dir",
            str(tmp_path / "missing"),
        ]
    )

    assert '"actual_data_mode": "blocked"' in output.read_text(encoding="utf-8")
