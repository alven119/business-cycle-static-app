from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_boom_ending_watch_overlay_script_reuses_existing_output(tmp_path: Path) -> None:
    output = write_report(tmp_path)

    completed = run_script("--output", str(output), "--reuse-existing")

    assert completed.returncode == 0, completed.stderr
    assert "experiment_id=boom_ending_watch_overlay_v1" in completed.stdout
    assert "global_watch_density_ratio=" in completed.stdout
    assert "output=" in completed.stdout
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["scenario_count"] == 1
    assert payload["acceptance_summary"]["pass_count"] == 1


def test_run_boom_ending_watch_overlay_script_accepts_custom_spec_with_reuse(tmp_path: Path) -> None:
    output = write_report(tmp_path)
    spec = write_spec(tmp_path)

    completed = run_script("--spec", str(spec), "--output", str(output), "--reuse-existing")

    assert completed.returncode == 0, completed.stderr
    assert "scenario_count=1" in completed.stdout


def test_run_boom_ending_watch_overlay_missing_spec_fails(tmp_path: Path) -> None:
    completed = run_script("--spec", str(tmp_path / "missing.yaml"), "--output", str(tmp_path / "out.json"))

    assert completed.returncode != 0
    assert "boom ending watch overlay spec does not exist" in completed.stderr


def write_report(tmp_path: Path) -> Path:
    path = tmp_path / "overlay.json"
    path.write_text(
        json.dumps(
            {
                "experiment_id": "boom_ending_watch_overlay_v1",
                "scenario_count": 1,
                "scenario_summaries": [
                    {
                        "scenario_id": "dotcom_bubble",
                        "first_watch_as_of": "2000-01-31",
                        "first_original_confirmed_recession_as_of": "2001-01-31",
                        "watch_lead_time_months": 12,
                    }
                ],
                "acceptance_summary": {
                    "pass_count": 1,
                    "warning_count": 0,
                    "fail_count": 0,
                    "dotcom_has_pre_recession_watch": True,
                    "gfc_has_pre_recession_watch": False,
                    "euro_debt_excessive_watch": False,
                    "late_cycle_2018_excessive_watch": False,
                },
                "global_watch_density_summary": {
                    "watch_density_ratio": 0.25,
                    "strong_density_ratio": 0.0,
                },
                "caveats_zh": [
                    "使用修訂後歷史資料，不等同當時投資人可見資料。",
                    "boom ending watch 不等於 confirmed recession。",
                    "不構成投資建議。",
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def write_spec(tmp_path: Path) -> Path:
    path = tmp_path / "overlay.yaml"
    path.write_text(
        """
boom_ending_watch_overlay_experiment:
  version: 1
  status: experimental
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 此為 experimental overlay，不代表正式模型已更新。
    - boom ending watch 不等於 confirmed recession。
    - 外生衝擊案例中，boom ending 指標可能是同步壓力反映，不代表事前預測。
    - 不構成投資建議。
  inputs:
    scenario_spec: specs/backtests/scenarios.yaml
    boom_ending_candidate_spec: specs/backtests/boom_ending_candidate_indicators.yaml
    boom_ending_watch_rule: specs/backtests/boom_ending_watch_rule.yaml
    boom_ending_refinement_experiment: specs/backtests/boom_ending_scoring_refinement_experiment.yaml
  overlay_policy: {}
  evaluation: {}
  acceptance_targets: []
""",
        encoding="utf-8",
    )
    return path


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_boom_ending_watch_overlay.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
