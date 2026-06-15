from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_score_boom_ending_candidates_script_with_fake_cache(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path)
    cache_dir = tmp_path / "fred"
    cache_dir.mkdir()
    write_series(cache_dir / "T10Y3M.csv", [1.0] * 70 + [-0.5] * 20)
    output_path = tmp_path / "scores.json"

    completed = run_script(
        "--as-of",
        "2022-06-30",
        "--spec",
        str(spec_path),
        "--cache-dir",
        str(cache_dir),
        "--output",
        str(output_path),
    )

    assert completed.returncode == 0, completed.stderr
    assert "as_of=2022-06-30" in completed.stdout
    assert "total_candidates=1" in completed.stdout
    assert "scored_candidates=1" in completed.stdout
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["scores"][0]["indicator_id"] == "yield_curve_10y_3m"
    assert payload["scores"][0]["score"] >= 70


def test_score_boom_ending_candidates_missing_series_warns_without_crash(
    tmp_path: Path,
) -> None:
    spec_path = write_spec(tmp_path)
    output_path = tmp_path / "scores.json"

    completed = run_script(
        "--as-of",
        "2022-06-30",
        "--spec",
        str(spec_path),
        "--cache-dir",
        str(tmp_path / "missing"),
        "--output",
        str(output_path),
    )

    assert completed.returncode == 0, completed.stderr
    assert "scored_candidates=0" in completed.stdout
    assert "failed_candidates=1" in completed.stdout
    assert "warnings=1" in completed.stdout
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["failures"][0]["error_type"] == "MissingRawCsv"


def test_score_boom_ending_candidates_as_of_is_required() -> None:
    completed = run_script()

    assert completed.returncode != 0
    assert "--as-of" in completed.stderr


def write_spec(tmp_path: Path) -> Path:
    path = tmp_path / "boom_candidates.yaml"
    path.write_text(
        """
boom_ending_candidate_indicators:
  version: 1
  status: test
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  indicators:
    - indicator_id: yield_curve_10y_3m
      display_name_zh: curve
      purpose_group: boom_ending
      provider: fred
      candidate_fred_series: [T10Y3M]
      preferred_series: T10Y3M
      transformation: [level]
      proposed_score_method: yield_curve_inversion_pressure_score
      expected_phase_impact: {boom: pressure}
      implementation_priority: high
""",
        encoding="utf-8",
    )
    return path


def write_series(path: Path, values: list[float]) -> None:
    rows = ["date,value"]
    for date, value in zip(months(len(values)), values):
        rows.append(f"{date},{value}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def months(count: int) -> list[str]:
    import pandas as pd

    return [item.date().isoformat() for item in pd.date_range("2015-01-31", periods=count, freq="ME")]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/score_boom_ending_candidates.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
