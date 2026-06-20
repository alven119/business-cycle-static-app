from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_recovery_refinement_experiment_script_succeeds(tmp_path: Path) -> None:
    paths = write_fixture(tmp_path)
    output = tmp_path / "out.json"

    completed = run_script(
        "--experiment",
        str(paths["experiment"]),
        "--windows",
        str(paths["windows"]),
        "--candidate-spec",
        str(paths["spec"]),
        "--cache-dir",
        str(paths["cache"]),
        "--output",
        str(output),
    )

    assert completed.returncode == 0, completed.stderr
    assert "euro_debt_false_strong_fixed=" in completed.stdout
    assert "policy_only_strong_blocked=" in completed.stdout
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["experiment_id"] == "test_recovery_refined"
    assert payload["point_count"] == 1
    assert "summary" in payload


def test_run_recovery_refinement_experiment_missing_experiment_fails(tmp_path: Path) -> None:
    completed = run_script("--experiment", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "does not exist" in completed.stderr


def test_run_recovery_refinement_experiment_missing_baseline_fails(tmp_path: Path) -> None:
    paths = write_fixture(tmp_path, write_baseline=False)

    completed = run_script(
        "--experiment",
        str(paths["experiment"]),
        "--windows",
        str(paths["windows"]),
        "--candidate-spec",
        str(paths["spec"]),
        "--cache-dir",
        str(paths["cache"]),
    )

    assert completed.returncode != 0
    assert "run scripts/run_recovery_diagnostics.py first" in completed.stderr


def write_fixture(tmp_path: Path, *, write_baseline: bool = True) -> dict[str, Path]:
    cache = tmp_path / "cache"
    cache.mkdir()
    write_series(cache / "ICSA.csv", [120, 140, 180, 220, 210, 190, 170, 155])
    write_series(cache / "RRSFS.csv", [100, 95, 92, 90, 91, 93, 95, 97])
    spec = tmp_path / "recovery_candidates.yaml"
    spec.write_text(
        """
recovery_candidate_indicators:
  version: 1
  status: experimental
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  indicators:
    - indicator_id: initial_jobless_claims_peak_reversal
      display_name_zh: 初領失業救濟金高點反轉
      purpose_group: recession_trough_recovery
      provider: fred
      candidate_fred_series: [ICSA]
      preferred_series: ICSA
      transformation: [moving_average]
      proposed_score_method: peak_reversal_score
      expected_phase_impact: {recovery: test}
      implementation_priority: high
    - indicator_id: real_retail_sales_bottoming
      display_name_zh: 實質零售銷售落底回升
      purpose_group: recession_trough_recovery
      provider: fred
      candidate_fred_series: [RRSFS]
      preferred_series: RRSFS
      transformation: [moving_average]
      proposed_score_method: bottoming_momentum_score
      expected_phase_impact: {recovery: test}
      implementation_priority: high
""",
        encoding="utf-8",
    )
    windows = tmp_path / "windows.yaml"
    windows.write_text(
        """
recovery_diagnostic_windows:
  version: 1
  status: experimental
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 此為 experimental diagnostics，不代表正式模型已更新。
    - recovery watch 不等於正式復甦確認。
    - policy easing 不得單獨確認 recovery。
    - 不構成投資建議。
  diagnostic_points:
    - scenario_id: test
      as_of: "2020-08-31"
      label: test_recovery
      expected_status: watch_or_strong
      reason_zh: test
      context:
        recent_formal_recession_phase: true
        recent_recession_candidate_watch_or_confirmed: true
        recession_depth_proxy_score: 80
        exogenous_shock_caveat: false
""",
        encoding="utf-8",
    )
    baseline = tmp_path / "baseline.json"
    if write_baseline:
        baseline.write_text(
            json.dumps(
                {
                    "points": [
                        {
                            "scenario_id": "test",
                            "as_of": "2020-08-31",
                            "label": "test_recovery",
                            "recovery_status": "weak",
                            "candidate_summary": {"weighted_recovery_score": 50.0},
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
    experiment = tmp_path / "experiment.yaml"
    experiment.write_text(
        f"""
recovery_scoring_refinement_experiment:
  version: 1
  status: experimental
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 此為 experimental scoring refinement，不代表正式模型已更新。
    - recovery watch 不等於正式復甦確認。
    - policy easing 不得單獨確認 recovery。
    - 不構成投資建議。
  inputs:
    recovery_candidate_spec: {spec}
    recovery_diagnostic_windows: {windows}
    baseline_diagnostics: {baseline}
  refined_profile:
    profile_id: test_recovery_refined
    recession_context_gate:
      enabled: true
      min_recession_depth_score: 60
    support_signal_cap:
      enabled: true
      policy_financial_only_max_status: weak
    labor_reversal:
      slow_recovery_sensitivity: true
    real_activity_bottoming:
      allow_slow_recovery_momentum: true
    exogenous_shock_profile:
      enabled: true
      max_status_without_labor_confirmation: watch
  expected_refinement_outcomes:
    - scenario_id: test
      as_of: "2020-08-31"
      label: test_recovery
      expected_min_status: weak
""",
        encoding="utf-8",
    )
    return {"cache": cache, "spec": spec, "windows": windows, "baseline": baseline, "experiment": experiment}


def write_series(path: Path, values: list[float]) -> None:
    dates = [f"2020-{month:02d}-29" for month in range(1, len(values) + 1)]
    path.write_text("date,value\n" + "\n".join(f"{date},{value}" for date, value in zip(dates, values, strict=True)), encoding="utf-8")


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_recovery_refinement_experiment.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
