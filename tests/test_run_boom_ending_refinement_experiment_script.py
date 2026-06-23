from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_run_boom_ending_refinement_experiment_script_succeeds(tmp_path: Path) -> None:
    windows = write_windows(tmp_path)
    groups = write_groups(tmp_path)
    spec = write_spec(tmp_path)
    baseline = write_baseline(tmp_path)
    experiment = write_experiment(tmp_path, baseline)
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    write_series(cache_dir / "T10Y3M.csv", [1.0] * 60 + [-0.5] * 12 + [0.2] * 6)
    output = tmp_path / "refinement.json"

    completed = run_script(
        "--experiment",
        str(experiment),
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
    assert "experiment_id=boom_ending_refined_v1" in completed.stdout
    assert "point_count=1" in completed.stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["point_count"] == 1
    assert payload["summary"]["expected_pass_count"] == 1


def test_run_boom_ending_refinement_experiment_custom_path_can_be_used(tmp_path: Path) -> None:
    windows = write_windows(tmp_path)
    groups = write_groups(tmp_path)
    spec = write_spec(tmp_path)
    baseline = write_baseline(tmp_path)
    experiment = write_experiment(tmp_path, baseline)
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    write_series(cache_dir / "T10Y3M.csv", [1.0] * 60 + [-0.5] * 12 + [0.2] * 6)
    output = tmp_path / "custom_refinement.json"

    completed = run_script(
        "--experiment",
        str(experiment),
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
    assert "gfc_2006_improved_to_watch=" in completed.stdout
    assert output.exists()
    assert not Path(
        "data/backtests/candidate_indicators/boom_ending_refinement/"
        "boom_ending_refinement_experiment.json"
    ).exists()


def test_run_boom_ending_refinement_experiment_missing_experiment_fails(tmp_path: Path) -> None:
    completed = run_script("--experiment", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Boom ending scoring refinement experiment file does not exist" in completed.stderr


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
        - as_of: "2021-06-30"
          label: gfc_yield_curve_warning
          expected_zh: early
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
    path = tmp_path / "spec.yaml"
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


def write_baseline(tmp_path: Path) -> Path:
    path = tmp_path / "baseline.json"
    path.write_text(
        json.dumps(
            {
                "points": [
                    {
                        "scenario_id": "global_financial_crisis",
                        "as_of": "2021-06-30",
                        "label": "gfc_yield_curve_warning",
                        "candidate_summary": {
                            "boom_ending_status": "none",
                            "weighted_boom_ending_score": 20.0,
                            "broad_group_count": 0,
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def write_experiment(tmp_path: Path, baseline: Path) -> Path:
    path = tmp_path / "experiment.yaml"
    path.write_text(
        f"""
boom_ending_scoring_refinement_experiment:
  version: 1
  status: experimental
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  baseline:
    diagnostics_path: {baseline}
  refined_profile:
    profile_id: boom_ending_refined_v1
    yield_curve:
      inversion_lookback_months: 18
      sustained_inversion_min_share: 0.6
      peak_warning_months_after_inversion: [3, 18]
  expected_refinement_outcomes:
    - scenario_id: global_financial_crisis
      as_of: "2021-06-30"
      expected_min_status: weak
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
        }
    )
    frame.to_csv(path, index=False)


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_boom_ending_refinement_experiment.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
