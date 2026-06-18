from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_boom_ending_attribution_script_succeeds(tmp_path: Path) -> None:
    diagnostics = write_diagnostics(tmp_path)
    output = tmp_path / "attribution.json"

    completed = run_script("--diagnostics", str(diagnostics), "--output", str(output))

    assert completed.returncode == 0, completed.stderr
    assert "point_count=1" in completed.stdout
    assert "refinement_candidate_count=" in completed.stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["point_count"] == 1
    assert payload["refinement_candidates"]


def test_run_boom_ending_attribution_missing_diagnostics_fails(tmp_path: Path) -> None:
    completed = run_script("--diagnostics", str(tmp_path / "missing.json"))

    assert completed.returncode != 0
    assert "Run scripts/run_boom_ending_diagnostics.py first" in completed.stderr


def write_diagnostics(tmp_path: Path) -> Path:
    path = tmp_path / "diagnostics.json"
    payload = {
        "data_mode": "revised",
        "points": [
            {
                "scenario_id": "global_financial_crisis",
                "as_of": "2006-12-31",
                "label": "gfc_yield_curve_warning",
                "candidate_summary": {
                    "boom_ending_status": "weak",
                    "weighted_boom_ending_score": 52.0,
                },
                "top_candidate_scores": [
                    {"indicator_id": "yield_curve_10y_3m", "score": 78, "confidence": 1.0},
                    {"indicator_id": "credit_spread_baa_10y", "score": 42, "confidence": 0.8},
                ],
                "group_summary": [],
            }
        ],
        "aggregate": {"candidate_indicators_requiring_refinement": ["credit_spread_baa_10y"]},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_boom_ending_attribution.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
