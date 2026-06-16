from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_run_boom_ending_diagnostics_script_succeeds(tmp_path: Path) -> None:
    windows = write_windows(tmp_path)
    spec = write_spec(tmp_path)
    groups = write_groups(tmp_path)
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    write_series(cache_dir / "T10Y3M.csv", [1.0] * 70 + [-0.5] * 20)
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


def test_run_boom_ending_diagnostics_custom_windows_can_be_used(tmp_path: Path) -> None:
    windows = write_windows(tmp_path)
    spec = write_spec(tmp_path)
    groups = write_groups(tmp_path)
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    write_series(cache_dir / "T10Y3M.csv", [1.0] * 70 + [-0.5] * 20)

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
    assert "gfc_2006_status=" in completed.stdout


def test_run_boom_ending_diagnostics_missing_windows_fails(tmp_path: Path) -> None:
    completed = run_script("--windows", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Boom ending diagnostics file does not exist" in completed.stderr


def write_windows(tmp_path: Path) -> Path:
    path = tmp_path / "windows.yaml"
    path.write_text(
        """
boom_ending_diagnostic_windows:
  version: 1
  status: test
  data_mode: revised
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  scenarios:
    global_financial_crisis:
      display_name_zh: 金融海嘯
      diagnostic_points:
        - as_of: "2022-06-30"
          label: gfc_yield_curve_warning
          expected_zh: early
        - as_of: "2022-06-30"
          label: gfc_confirmed_recession
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
  rates_policy:
    - yield_curve_10y_3m
""",
        encoding="utf-8",
    )
    return path


def write_spec(tmp_path: Path) -> Path:
    path = tmp_path / "candidates.yaml"
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
      display_name_zh: 10 年期與 3 個月期公債利差
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
        [sys.executable, "scripts/run_boom_ending_diagnostics.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
