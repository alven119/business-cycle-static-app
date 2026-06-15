from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import scripts.run_calibration_experiment as script


def test_run_calibration_experiment_script_runs_one_period(tmp_path: Path) -> None:
    output_dir = tmp_path / "calibration"
    completed = run_script(
        "--experiment-id",
        "test",
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "1",
        "--output-dir",
        str(output_dir),
    )

    summary_path = output_dir / "test" / "calibration_summary.json"
    assert completed.returncode == 0, completed.stderr
    assert "experiment_id=test" in completed.stdout
    assert "scenario_count=1" in completed.stdout
    assert summary_path.exists()


def test_run_calibration_experiment_script_scenario_id_runs_single(tmp_path: Path) -> None:
    output_dir = tmp_path / "calibration"
    completed = run_script(
        "--experiment-id",
        "single",
        "--scenario-id",
        "global_financial_crisis",
        "--max-periods",
        "1",
        "--output-dir",
        str(output_dir),
    )

    payload = json.loads((output_dir / "single" / "calibration_summary.json").read_text(encoding="utf-8"))
    assert completed.returncode == 0, completed.stderr
    assert payload["scenario_count"] == 1
    assert payload["scenarios"][0]["scenario_id"] == "global_financial_crisis"


def test_run_calibration_experiment_missing_controls_fails(tmp_path: Path) -> None:
    completed = run_script(
        "--experiment-id",
        "test",
        "--scenario-id",
        "global_financial_crisis",
        "--controls",
        str(tmp_path / "missing.yaml"),
        "--output-dir",
        str(tmp_path / "calibration"),
    )

    assert completed.returncode != 0
    assert "transition controls config does not exist" in completed.stderr


def test_run_calibration_experiment_unknown_scenario_fails(tmp_path: Path) -> None:
    completed = run_script(
        "--experiment-id",
        "test",
        "--scenario-id",
        "missing",
        "--output-dir",
        str(tmp_path / "calibration"),
    )

    assert completed.returncode != 0
    assert "Unknown scenario_id: missing" in completed.stderr


def test_run_calibration_experiment_reuse_and_force_flags(monkeypatch, capsys) -> None:  # noqa: ANN001
    calls: list[dict] = []

    def fake_run_calibration_experiment(**kwargs) -> dict:  # noqa: ANN003
        calls.append(kwargs)
        return {
            "experiment_id": kwargs["experiment_id"],
            "scenario_count": 1,
            "aggregate": {
                "baseline_total_plausibility_warning_count": 1,
                "experiment_total_plausibility_warning_count": 1,
                "delta_total_plausibility_warning_count": 0,
                "scenario_improved_count": 0,
                "scenario_regressed_count": 0,
                "scenario_with_failures_count": 0,
            },
            "reuse": {"reused_output_count": 4, "recomputed_output_count": 0},
            "output_path": "tmp/summary.json",
        }

    monkeypatch.setattr(script, "run_calibration_experiment", fake_run_calibration_experiment)

    exit_code = script.main(["--experiment-id", "test", "--reuse-existing", "--force"])

    assert exit_code == 0
    assert calls[0]["reuse_existing"] is True
    assert calls[0]["force"] is True
    assert "reused_output_count=4" in capsys.readouterr().out


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_calibration_experiment.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
