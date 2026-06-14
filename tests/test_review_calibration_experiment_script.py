from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_review_calibration_experiment_script_with_experiment_id(tmp_path: Path) -> None:
    experiment_dir = tmp_path / "data" / "backtests" / "calibration" / "test"
    experiment_dir.mkdir(parents=True)
    write_summary(experiment_dir / "calibration_summary.json")
    windows_path = tmp_path / "windows.yaml"
    write_windows(windows_path)

    completed = run_script(
        "--experiment-id",
        "test",
        "--windows",
        str(windows_path),
        cwd=tmp_path,
    )

    output_path = experiment_dir / "calibration_acceptance_review.json"
    assert completed.returncode == 0, completed.stderr
    assert "experiment_id=test" in completed.stdout
    assert "scenario_count=1" in completed.stdout
    assert output_path.exists()


def test_review_calibration_experiment_script_custom_paths(tmp_path: Path) -> None:
    summary_path = tmp_path / "summary.json"
    windows_path = tmp_path / "windows.yaml"
    output_path = tmp_path / "review.json"
    write_summary(summary_path)
    write_windows(windows_path)

    completed = run_script(
        "--experiment-id",
        "custom",
        "--summary",
        str(summary_path),
        "--windows",
        str(windows_path),
        "--output",
        str(output_path),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert completed.returncode == 0, completed.stderr
    assert payload["scenario_count"] == 1
    assert payload["aggregate"]["needs_longer_horizon_count"] == 1


def test_review_calibration_experiment_missing_summary_fails(tmp_path: Path) -> None:
    windows_path = tmp_path / "windows.yaml"
    write_windows(windows_path)

    completed = run_script(
        "--experiment-id",
        "missing",
        "--summary",
        str(tmp_path / "missing.json"),
        "--windows",
        str(windows_path),
    )

    assert completed.returncode != 0
    assert "calibration summary does not exist" in completed.stderr


def test_review_calibration_experiment_missing_windows_fails(tmp_path: Path) -> None:
    summary_path = tmp_path / "summary.json"
    write_summary(summary_path)

    completed = run_script(
        "--experiment-id",
        "missing_windows",
        "--summary",
        str(summary_path),
        "--windows",
        str(tmp_path / "missing.yaml"),
    )

    assert completed.returncode != 0
    assert "acceptance windows does not exist" in completed.stderr


def write_summary(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "experiment_id": "test",
                "data_mode": "revised",
                "max_periods": 12,
                "scenarios": [
                    {
                        "scenario_id": "global_financial_crisis",
                        "display_name_zh": "金融海嘯",
                        "experiment": {"first_recession_current_as_of": None},
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def write_windows(path: Path) -> None:
    path.write_text(
        """
acceptance_windows:
  version: 1
  data_mode: revised
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 此為模型校準驗收輔助，不構成投資建議。
    - 驗收窗口只用於模型診斷，不代表唯一正確答案。
  scenarios:
    global_financial_crisis:
      display_name_zh: 金融海嘯
      expected_behavior_zh: 2005 年不應過早確認衰退；完整窗口應於 2007/2008 附近升高衰退風險。
      early_false_recession_before: "2007-01-01"
      expected_recession_window:
        start: "2007-01-01"
        end: "2009-06-30"
      allow_no_recession_in_first_12_periods: true
""".lstrip(),
        encoding="utf-8",
    )


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, str(project_root / "scripts" / "review_calibration_experiment.py"), *args],
        cwd=cwd or project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
