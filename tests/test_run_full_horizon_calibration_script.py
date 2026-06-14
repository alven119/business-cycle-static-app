from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import scripts.run_full_horizon_calibration as script


def test_run_full_horizon_calibration_script_runs(monkeypatch, tmp_path: Path, capsys) -> None:  # noqa: ANN001
    def fake_run_full_horizon_calibration(**kwargs) -> dict:  # noqa: ANN003
        output = tmp_path / "review.json"
        output.write_text(
            json.dumps(
                {
                    "scenario_count": 1,
                    "aggregate": {
                        "pass_count": 1,
                        "warning_count": 0,
                        "fail_count": 0,
                        "needs_longer_horizon_count": 0,
                        "early_false_recession_count": 0,
                    },
                }
            ),
            encoding="utf-8",
        )
        return {
            "experiment_id": kwargs["experiment_id"],
            "aggregate": {"scenario_with_failures_count": 0},
            "acceptance_review_path": str(output),
        }

    monkeypatch.setattr(script, "run_full_horizon_calibration", fake_run_full_horizon_calibration)

    exit_code = script.main(["--experiment-id", "test"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "experiment_id=test" in captured.out
    assert "pass_count=1" in captured.out


def test_run_full_horizon_calibration_script_scenario_id(monkeypatch, capsys) -> None:  # noqa: ANN001
    calls: list[dict] = []

    def fake_run_full_horizon_calibration(**kwargs) -> dict:  # noqa: ANN003
        calls.append(kwargs)
        review_path = Path(kwargs["output_dir"]) / kwargs["experiment_id"] / "review.json"
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(
            json.dumps(
                {
                    "scenario_count": 1,
                    "aggregate": {
                        "pass_count": 1,
                        "warning_count": 0,
                        "fail_count": 0,
                        "needs_longer_horizon_count": 0,
                        "early_false_recession_count": 0,
                    },
                }
            ),
            encoding="utf-8",
        )
        return {
            "experiment_id": kwargs["experiment_id"],
            "aggregate": {"scenario_with_failures_count": 0},
            "acceptance_review_path": str(review_path),
        }

    monkeypatch.setattr(script, "run_full_horizon_calibration", fake_run_full_horizon_calibration)

    exit_code = script.main(["--experiment-id", "test", "--scenario-id", "covid_recession"])

    assert exit_code == 0
    assert calls[0]["scenario_id"] == "covid_recession"
    assert "scenario_count=1" in capsys.readouterr().out


def test_run_full_horizon_calibration_script_accepts_breadth_controls(monkeypatch, capsys) -> None:  # noqa: ANN001
    calls: list[dict] = []

    def fake_run_full_horizon_calibration(**kwargs) -> dict:  # noqa: ANN003
        calls.append(kwargs)
        review_path = Path(kwargs["output_dir"]) / kwargs["experiment_id"] / "review.json"
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(
            json.dumps(
                {
                    "scenario_count": 1,
                    "aggregate": {
                        "pass_count": 1,
                        "warning_count": 0,
                        "fail_count": 0,
                        "needs_longer_horizon_count": 0,
                        "early_false_recession_count": 0,
                    },
                }
            ),
            encoding="utf-8",
        )
        return {
            "experiment_id": kwargs["experiment_id"],
            "aggregate": {"scenario_with_failures_count": 0},
            "acceptance_review_path": str(review_path),
        }

    monkeypatch.setattr(script, "run_full_horizon_calibration", fake_run_full_horizon_calibration)

    exit_code = script.main(
        [
            "--experiment-id",
            "test",
            "--controls",
            "specs/backtests/transition_controls_recession_breadth_experiment.yaml",
        ]
    )

    assert exit_code == 0
    assert calls[0]["controls_config_path"] == "specs/backtests/transition_controls_recession_breadth_experiment.yaml"
    assert "pass_count=1" in capsys.readouterr().out


def test_run_full_horizon_calibration_missing_controls_fails(tmp_path: Path) -> None:
    completed = run_script(
        "--experiment-id",
        "test",
        "--controls",
        str(tmp_path / "missing.yaml"),
        "--output-dir",
        str(tmp_path / "calibration"),
    )

    assert completed.returncode != 0
    assert "transition controls config does not exist" in completed.stderr


def test_run_full_horizon_calibration_unknown_scenario_fails(tmp_path: Path) -> None:
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


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    script_path = project_root / "scripts" / "run_full_horizon_calibration.py"
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
