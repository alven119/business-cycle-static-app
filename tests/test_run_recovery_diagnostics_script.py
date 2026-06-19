from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_run_recovery_diagnostics_script_succeeds(tmp_path: Path) -> None:
    windows = write_windows(tmp_path)
    spec = write_spec(tmp_path)
    groups = write_groups(tmp_path)
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    write_series(cache_dir / "ICSA.csv", [220.0] * 40 + [520.0] * 8 + [500.0, 460.0, 420.0, 380.0])
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
    assert "diagnostic_point_count=1" in completed.stdout
    assert "policy_only_warning_count=" in completed.stdout
    assert "missed_recovery_watch_points=" in completed.stdout
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["diagnostic_point_count"] == 1
    assert payload["points"][0]["candidate_summary"]["total_candidates"] == 1


def test_run_recovery_diagnostics_accepts_custom_paths(tmp_path: Path) -> None:
    windows = write_windows(tmp_path)
    spec = write_spec(tmp_path)
    groups = write_groups(tmp_path)
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    write_series(cache_dir / "ICSA.csv", [220.0] * 40 + [520.0] * 8 + [500.0, 460.0, 420.0, 380.0])

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
    assert "match_count=" in completed.stdout


def test_run_recovery_diagnostics_missing_windows_fails(tmp_path: Path) -> None:
    completed = run_script("--windows", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Recovery diagnostics file does not exist" in completed.stderr


def write_windows(tmp_path: Path) -> Path:
    path = tmp_path / "windows.yaml"
    path.write_text(
        """
recovery_diagnostic_windows:
  version: 1
  status: test
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - recovery watch 不等於正式復甦確認。
    - policy easing 不得單獨確認 recovery。
    - 不構成投資建議。
  diagnostic_points:
    - scenario_id: global_financial_crisis
      as_of: "2021-01-29"
      label: gfc_trough_area
      expected_status: watch_or_strong
      reason_zh: test
""",
        encoding="utf-8",
    )
    return path


def write_groups(tmp_path: Path) -> Path:
    path = tmp_path / "groups.yaml"
    path.write_text(
        """
experimental_indicator_groups:
  labor_reversal:
    - initial_jobless_claims_peak_reversal
""",
        encoding="utf-8",
    )
    return path


def write_spec(tmp_path: Path) -> Path:
    path = tmp_path / "candidates.yaml"
    path.write_text(
        """
recovery_candidate_indicators:
  version: 1
  status: test
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  indicators:
    - indicator_id: initial_jobless_claims_peak_reversal
      display_name_zh: claims
      purpose_group: recession_trough_recovery
      provider: fred
      candidate_fred_series: [ICSA]
      preferred_series: ICSA
      transformation: [moving_average]
      proposed_score_method: peak_reversal_score
      expected_phase_impact: {recovery: support}
      implementation_priority: high
""",
        encoding="utf-8",
    )
    return path


def write_series(path: Path, values: list[float]) -> None:
    frame = pd.DataFrame(
        {
            "series_id": path.stem,
            "date": pd.date_range("2020-01-03", periods=len(values), freq="W-FRI"),
            "value": values,
            "realtime_start": "2026-01-01",
            "realtime_end": "2026-01-01",
        }
    )
    frame.to_csv(path, index=False)


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_recovery_diagnostics.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
