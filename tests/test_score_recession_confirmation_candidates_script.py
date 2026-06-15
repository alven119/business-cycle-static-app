from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_score_recession_confirmation_candidates_script_writes_output(tmp_path: Path) -> None:
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    write_series(cache_dir / "CCSA.csv", [100 + i * 5 for i in range(80)])
    output = tmp_path / "candidate_indicator_scores.json"

    completed = run_script(
        "--as-of",
        "2020-12-31",
        "--cache-dir",
        str(cache_dir),
        "--output",
        str(output),
    )

    assert completed.returncode == 0, completed.stderr
    assert "as_of=2020-12-31" in completed.stdout
    assert "total_candidates=7" in completed.stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["as_of"] == "2020-12-31"
    assert payload["total_candidates"] == 7
    assert payload["scored_candidates"] == 1
    assert payload["failed_candidates"] == 6
    assert payload["scores"][0]["indicator_id"] == "continuing_jobless_claims"


def test_score_recession_confirmation_candidates_missing_series_warns_without_crash(tmp_path: Path) -> None:
    output = tmp_path / "candidate_indicator_scores.json"

    completed = run_script(
        "--as-of",
        "2019-02-28",
        "--cache-dir",
        str(tmp_path / "missing_cache"),
        "--output",
        str(output),
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["scored_candidates"] == 0
    assert payload["failed_candidates"] == 7
    assert payload["warnings"]


def test_score_recession_confirmation_candidates_missing_spec_fails(tmp_path: Path) -> None:
    completed = run_script(
        "--as-of",
        "2019-02-28",
        "--spec",
        str(tmp_path / "missing.yaml"),
    )

    assert completed.returncode != 0
    assert "Candidate indicator spec file does not exist" in completed.stderr


def write_series(path: Path, values: list[float]) -> None:
    frame = pd.DataFrame(
        {
            "series_id": path.stem,
            "date": pd.date_range("2015-01-31", periods=len(values), freq="ME"),
            "value": values,
            "realtime_start": "2026-01-01",
            "realtime_end": "2026-01-01",
        }
    )
    frame.to_csv(path, index=False)


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/score_recession_confirmation_candidates.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
