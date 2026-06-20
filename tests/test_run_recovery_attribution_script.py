from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_recovery_attribution_script_succeeds(tmp_path: Path) -> None:
    diagnostics = write_diagnostics(tmp_path)
    output = tmp_path / "attribution.json"

    completed = run_script("--diagnostics", str(diagnostics), "--output", str(output))

    assert completed.returncode == 0, completed.stderr
    assert "point_count=1" in completed.stdout
    assert "mismatch_count=1" in completed.stdout
    assert "refinement_candidate_count=" in completed.stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["point_count"] == 1
    assert payload["refinement_candidates"]


def test_run_recovery_attribution_missing_diagnostics_fails(tmp_path: Path) -> None:
    completed = run_script("--diagnostics", str(tmp_path / "missing.json"))

    assert completed.returncode != 0
    assert "Run scripts/run_recovery_diagnostics.py first" in completed.stderr


def write_diagnostics(tmp_path: Path) -> Path:
    path = tmp_path / "diagnostics.json"
    payload = {
        "data_mode": "revised",
        "points": [
            {
                "scenario_id": "euro_debt_slowdown",
                "as_of": "2011-12-31",
                "label": "euro_debt_non_recession",
                "expected_status": "weak_or_none",
                "recovery_status": "strong",
                "matches_expected": False,
                "candidate_summary": {
                    "weighted_recovery_score": 83.0,
                    "policy_only_signal": False,
                    "labor_confirmed": False,
                    "real_activity_confirmed": False,
                    "credit_financial_confirmed": True,
                },
                "top_positive_indicators": [
                    {"indicator_id": "financial_stress_easing", "score": 89, "confidence": 0.9},
                    {"indicator_id": "credit_spread_easing", "score": 78, "confidence": 0.8},
                ],
                "weak_but_important_indicators": [],
                "group_summary": [],
            }
        ],
        "summary": {
            "mismatch_count": 1,
            "indicators_requiring_refinement": ["financial_stress_easing"],
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_recovery_attribution.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
