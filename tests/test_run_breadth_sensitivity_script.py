from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import scripts.run_breadth_sensitivity as script


def test_run_breadth_sensitivity_script_runs(monkeypatch, capsys) -> None:  # noqa: ANN001
    def fake_runner(**kwargs) -> dict:  # noqa: ANN003
        return {
            "experiment_id": kwargs["experiment_id"],
            "variant_count": 2,
            "recommended_variants": ["v_pass"],
            "aggregate": {
                "variant_pass_count": 1,
                "variant_fail_count": 1,
                "variants_blocking_covid_false_recession": ["v_pass"],
            },
            "output_path": "tmp/summary.json",
        }

    monkeypatch.setattr(script, "run_breadth_sensitivity_experiment", fake_runner)

    exit_code = script.main(["--experiment-id", "test"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "experiment_id=test" in captured.out
    assert "variant_count=2" in captured.out
    assert "recommended_variants=['v_pass']" in captured.out


def test_run_breadth_sensitivity_script_variant_id(monkeypatch, capsys) -> None:  # noqa: ANN001
    calls: list[dict] = []

    def fake_runner(**kwargs) -> dict:  # noqa: ANN003
        calls.append(kwargs)
        return {
            "experiment_id": kwargs["experiment_id"],
            "variant_count": 1,
            "recommended_variants": [],
            "aggregate": {
                "variant_pass_count": 0,
                "variant_fail_count": 1,
                "variants_blocking_covid_false_recession": [],
            },
            "output_path": "tmp/summary.json",
        }

    monkeypatch.setattr(script, "run_breadth_sensitivity_experiment", fake_runner)

    exit_code = script.main(["--experiment-id", "test", "--variant-id", "v4_core_plus_financial"])

    assert exit_code == 0
    assert calls[0]["variant_id"] == "v4_core_plus_financial"
    assert "variant_count=1" in capsys.readouterr().out


def test_run_breadth_sensitivity_reuse_and_force_flags(monkeypatch, capsys) -> None:  # noqa: ANN001
    calls: list[dict] = []

    def fake_runner(**kwargs) -> dict:  # noqa: ANN003
        calls.append(kwargs)
        return {
            "experiment_id": kwargs["experiment_id"],
            "variant_count": 1,
            "recommended_variants": [],
            "aggregate": {
                "variant_pass_count": 0,
                "variant_fail_count": 1,
                "variants_blocking_covid_false_recession": [],
            },
            "reuse": {"reused_variant_count": 1, "recomputed_variant_count": 0},
            "output_path": "tmp/summary.json",
        }

    monkeypatch.setattr(script, "run_breadth_sensitivity_experiment", fake_runner)

    exit_code = script.main(["--experiment-id", "test", "--reuse-existing", "--force"])

    assert exit_code == 0
    assert calls[0]["reuse_existing"] is True
    assert calls[0]["force"] is True
    assert "reused_variant_count=1" in capsys.readouterr().out


def test_run_breadth_sensitivity_missing_matrix_fails(tmp_path: Path) -> None:
    completed = run_script("--experiment-id", "test", "--matrix", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Breadth sensitivity matrix does not exist" in completed.stderr


def test_run_breadth_sensitivity_unknown_variant_fails(tmp_path: Path) -> None:
    output_dir = tmp_path / "sensitivity"
    completed = run_script(
        "--experiment-id",
        "test",
        "--variant-id",
        "missing",
        "--output-dir",
        str(output_dir),
    )

    assert completed.returncode != 0
    assert "Unknown variant_id: missing" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    script_path = project_root / "scripts" / "run_breadth_sensitivity.py"
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
