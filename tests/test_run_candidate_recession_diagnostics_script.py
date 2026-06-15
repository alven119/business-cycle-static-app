from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_run_candidate_recession_diagnostics_script_succeeds(tmp_path: Path) -> None:
    windows = write_windows(tmp_path)
    spec = write_spec(tmp_path)
    groups = write_groups(tmp_path)
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    write_series(cache_dir / "CCSA.csv", [100 + i * 5 for i in range(80)])
    output = tmp_path / "diagnostics.json"

    completed = run_script(
        "--windows",
        str(windows),
        "--spec",
        str(spec),
        "--groups",
        str(groups),
        "--cache-dir",
        str(cache_dir),
        "--output",
        str(output),
    )

    assert completed.returncode == 0, completed.stderr
    assert "diagnostic_point_count=2" in completed.stdout
    assert "points_with_full_scores=2" in completed.stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["diagnostic_point_count"] == 2
    assert payload["points"][0]["candidate_summary"]["total_candidates"] == 1


def test_run_candidate_recession_diagnostics_custom_windows_can_be_used(tmp_path: Path) -> None:
    windows = write_windows(tmp_path)
    spec = write_spec(tmp_path)
    groups = write_groups(tmp_path)
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    write_series(cache_dir / "CCSA.csv", [100 + i * 5 for i in range(80)])

    completed = run_script(
        "--windows",
        str(windows),
        "--spec",
        str(spec),
        "--groups",
        str(groups),
        "--cache-dir",
        str(cache_dir),
    )

    assert completed.returncode == 0, completed.stderr
    assert "covid_2019_status=" in completed.stdout


def test_run_candidate_recession_diagnostics_missing_windows_fails(tmp_path: Path) -> None:
    completed = run_script("--windows", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Candidate recession diagnostics file does not exist" in completed.stderr


def write_windows(tmp_path: Path) -> Path:
    path = tmp_path / "windows.yaml"
    path.write_text(
        """
candidate_recession_diagnostic_windows:
  version: 1
  status: test
  data_mode: revised
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  scenarios:
    covid_recession:
      display_name_zh: COVID 衰退
      diagnostic_points:
        - as_of: "2021-12-31"
          label: covid_false_positive_candidate
          expected_zh: weak
        - as_of: "2025-12-31"
          label: covid_true_recession_candidate
          expected_zh: strong
""",
        encoding="utf-8",
    )
    return path


def write_groups(tmp_path: Path) -> Path:
    path = tmp_path / "groups.yaml"
    path.write_text(
        """
experimental_indicator_groups:
  employment:
    - continuing_jobless_claims
""",
        encoding="utf-8",
    )
    return path


def write_spec(tmp_path: Path) -> Path:
    path = tmp_path / "candidates.yaml"
    path.write_text(
        """
recession_confirmation_candidate_indicators:
  version: 1
  status: test
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  indicators:
    - indicator_id: continuing_jobless_claims
      display_name_zh: 續領失業救濟金人數
      purpose_group: recession_confirmation
      provider: fred
      candidate_fred_series: [CCSA]
      preferred_series: CCSA
      transformation: [moving_average]
      proposed_score_method: sustained_deterioration_score
      expected_phase_impact: {recession: stress}
      implementation_priority: high
""",
        encoding="utf-8",
    )
    return path


def write_series(path: Path, values: list[float]) -> None:
    frame = pd.DataFrame(
        {
            "series_id": path.stem,
            "date": pd.date_range("2019-01-31", periods=len(values), freq="ME"),
            "value": values,
            "realtime_start": "2026-01-01",
            "realtime_end": "2026-01-01",
        }
    )
    frame.to_csv(path, index=False)


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_candidate_recession_diagnostics.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
