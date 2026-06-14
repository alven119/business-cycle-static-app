from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_diagnose_covid_false_positive_script_success(tmp_path: Path) -> None:
    write_fixture(tmp_path, "test")

    completed = run_script("--experiment-id", "test", "--experiment-root", str(tmp_path / "calibration"))

    output_path = tmp_path / "calibration" / "test" / "covid_false_positive_diagnostic.json"
    assert completed.returncode == 0, completed.stderr
    assert "experiment_id=test" in completed.stdout
    assert "scenario_id=covid_recession" in completed.stdout
    assert "initial_jobless_claims" in completed.stdout
    assert output_path.exists()


def test_diagnose_covid_false_positive_script_missing_experiment_fails(tmp_path: Path) -> None:
    completed = run_script(
        "--experiment-id",
        "missing",
        "--experiment-root",
        str(tmp_path / "calibration"),
    )

    assert completed.returncode != 0
    assert "missing COVID false-positive diagnostic input" in completed.stderr


def write_fixture(root: Path, experiment_id: str) -> None:
    experiment_root = root / "calibration" / experiment_id
    scenario_dir = experiment_root / "experiment" / "covid_recession"
    write_json(
        experiment_root / "calibration_summary.json",
        {
            "experiment_id": experiment_id,
            "data_mode": "revised",
            "scenarios": [
                {
                    "scenario_id": "covid_recession",
                    "experiment": {"first_recession_current_as_of": "2019-02-28"},
                }
            ],
            "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
        },
    )
    write_json(
        experiment_root / "calibration_acceptance_review.json",
        {
            "scenarios": [
                {
                    "scenario_id": "covid_recession",
                    "first_recession_current_as_of": "2019-02-28",
                    "early_false_recession": True,
                    "recession_timing_status": "too_early",
                    "acceptance_status": "fail",
                }
            ],
            "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
        },
    )
    write_json(
        scenario_dir / "timeline.json",
        {
            "scenario_id": "covid_recession",
            "display_name_zh": "COVID 衰退",
            "data_mode": "revised",
            "periods": [{"as_of": "2019-02-28"}],
            "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
        },
    )
    write_json(
        scenario_dir / "transition_attribution.json",
        {
            "diagnostics": [
                {
                    "as_of": "2019-02-28",
                    "top_indicator_score_changes": [
                        {"indicator_id": "initial_jobless_claims", "delta": 40.0}
                    ],
                }
            ],
            "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
        },
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    script_path = project_root / "scripts" / "diagnose_covid_false_positive.py"
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
