from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_boom_ending_watch_rule_script_succeeds(tmp_path: Path) -> None:
    refinement = write_refinement(tmp_path)
    output = tmp_path / "watch_rule.json"

    completed = run_script("--refinement", str(refinement), "--output", str(output))

    assert completed.returncode == 0, completed.stderr
    assert "match_count=" in completed.stdout
    assert "unexpected_strong_points=" in completed.stdout
    assert "missed_watch_points=" in completed.stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["point_count"] == 2
    assert payload["summary"]["match_count"] == 2


def test_run_boom_ending_watch_rule_custom_rule_can_be_used(tmp_path: Path) -> None:
    refinement = write_refinement(tmp_path)
    rule = write_rule(tmp_path)

    completed = run_script("--refinement", str(refinement), "--rule", str(rule))

    assert completed.returncode == 0, completed.stderr
    assert "watch_count=1" in completed.stdout


def test_run_boom_ending_watch_rule_missing_refinement_fails(tmp_path: Path) -> None:
    completed = run_script("--refinement", str(tmp_path / "missing.json"))

    assert completed.returncode != 0
    assert "Run scripts/run_boom_ending_refinement_experiment.py first" in completed.stderr


def write_refinement(tmp_path: Path) -> Path:
    path = tmp_path / "refinement.json"
    path.write_text(
        json.dumps(
            {
                "points": [
                    point("dotcom_bubble", "2000-03-31", "dotcom_market_peak_area", 68, 2, 3, 2, 2),
                    point("euro_debt_slowdown", "2011-12-31", "euro_debt_slowdown_warning", 48, 2, 2, 1, 0),
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def point(
    scenario_id: str,
    as_of: str,
    label: str,
    weighted_score: float,
    broad_groups: int,
    high_signals: int,
    high_confidence_high_signals: int,
    rates_policy_high_signals: int,
) -> dict:
    return {
        "scenario_id": scenario_id,
        "as_of": as_of,
        "label": label,
        "refined_score": weighted_score,
        "refined_broad_group_count": broad_groups,
        "refined_high_signal_count": high_signals,
        "refined_high_confidence_high_signal_count": high_confidence_high_signals,
        "refined_group_summary": [
            {
                "group_id": "rates_policy",
                "high_signal_count": rates_policy_high_signals,
            }
        ],
    }


def write_rule(tmp_path: Path) -> Path:
    source = Path("specs/backtests/boom_ending_watch_rule.yaml")
    target = tmp_path / "rule.yaml"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_boom_ending_watch_rule.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
