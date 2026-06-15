from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_candidate_recession_rule_script_succeeds(tmp_path: Path) -> None:
    diagnostics = write_diagnostics(tmp_path)
    output = tmp_path / "report.json"

    completed = run_script("--diagnostics", str(diagnostics), "--output", str(output))

    assert completed.returncode == 0, completed.stderr
    assert "point_count=2" in completed.stdout
    assert "match_count=2" in completed.stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["point_count"] == 2
    assert payload["summary"]["confirmed_count"] == 1
    assert payload["summary"]["watch_count"] == 1


def test_run_candidate_recession_rule_script_accepts_custom_rule(tmp_path: Path) -> None:
    diagnostics = write_diagnostics(tmp_path)
    custom_rule = tmp_path / "rule.yaml"
    custom_rule.write_text(
        Path("specs/backtests/candidate_recession_confirmation_rule.yaml")
        .read_text(encoding="utf-8")
        .replace("version: 1", "version: 2", 1),
        encoding="utf-8",
    )
    output = tmp_path / "report.json"

    completed = run_script("--diagnostics", str(diagnostics), "--rule", str(custom_rule), "--output", str(output))

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["rule_version"] == 2


def test_run_candidate_recession_rule_missing_diagnostics_fails(tmp_path: Path) -> None:
    completed = run_script("--diagnostics", str(tmp_path / "missing.json"))

    assert completed.returncode != 0
    assert "Run scripts/run_candidate_recession_diagnostics.py first" in completed.stderr


def write_diagnostics(tmp_path: Path) -> Path:
    path = tmp_path / "diagnostics.json"
    payload = {
        "points": [
            {
                "scenario_id": "covid_recession",
                "as_of": "2019-02-28",
                "label": "covid_false_positive_candidate",
                "candidate_summary": {
                    "weighted_confirmation_score": 61.0822,
                    "broad_group_count": 3,
                    "high_signal_count": 3,
                    "high_confidence_high_signal_count": 1,
                },
            },
            {
                "scenario_id": "covid_recession",
                "as_of": "2020-03-31",
                "label": "covid_true_recession_candidate",
                "candidate_summary": {
                    "weighted_confirmation_score": 92.8883,
                    "broad_group_count": 3,
                    "high_signal_count": 4,
                    "high_confidence_high_signal_count": 4,
                },
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_candidate_recession_rule.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
