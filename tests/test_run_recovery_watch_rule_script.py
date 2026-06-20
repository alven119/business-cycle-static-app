from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_recovery_watch_rule_script_succeeds(tmp_path: Path) -> None:
    refinement = write_refinement(tmp_path)
    output = tmp_path / "watch_rule.json"

    completed = run_script("--refinement", str(refinement), "--output", str(output))

    assert completed.returncode == 0, completed.stderr
    assert "match_count=" in completed.stdout
    assert "policy_only_blocked_count=" in completed.stdout
    assert "context_gate_blocked_count=" in completed.stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["point_count"] == 2
    assert payload["summary"]["match_count"] == 2


def test_run_recovery_watch_rule_custom_rule_can_be_used(tmp_path: Path) -> None:
    refinement = write_refinement(tmp_path)
    rule = write_rule(tmp_path)

    completed = run_script("--refinement", str(refinement), "--rule", str(rule))

    assert completed.returncode == 0, completed.stderr
    assert "recovery_watch_count=1" in completed.stdout


def test_run_recovery_watch_rule_missing_refinement_fails(tmp_path: Path) -> None:
    completed = run_script("--refinement", str(tmp_path / "missing.json"))

    assert completed.returncode != 0
    assert "Run scripts/run_recovery_refinement_experiment.py first" in completed.stderr


def write_refinement(tmp_path: Path) -> Path:
    path = tmp_path / "refinement.json"
    path.write_text(
        json.dumps(
            {
                "points": [
                    point("dotcom_bubble", "2002-03-31", "dotcom_recovery_initial", 68, 2, 3, 2),
                    point(
                        "euro_debt_slowdown",
                        "2011-12-31",
                        "euro_debt_non_recession",
                        82,
                        4,
                        5,
                        4,
                        recession_context=False,
                        context_gate_applied=True,
                    ),
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
    *,
    recession_context: bool = True,
    context_gate_applied: bool = False,
) -> dict:
    return {
        "scenario_id": scenario_id,
        "as_of": as_of,
        "label": label,
        "candidate_summary_before_caps": {
            "weighted_recovery_score": weighted_score,
            "broad_group_count": broad_groups,
            "high_signal_count": high_signals,
            "high_confidence_high_signal_count": high_confidence_high_signals,
            "policy_only_signal": False,
            "labor_confirmed": True,
            "real_activity_confirmed": True,
            "credit_financial_confirmed": True,
        },
        "support_cap_summary": {"support_only_cap_applied": False},
        "context_gate_summary": {
            "recession_context_detected": recession_context,
            "context_gate_applied": context_gate_applied,
            "exogenous_shock_caveat": False,
        },
        "context_gate_applied": context_gate_applied,
    }


def write_rule(tmp_path: Path) -> Path:
    source = Path("specs/backtests/recovery_watch_rule.yaml")
    target = tmp_path / "rule.yaml"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_recovery_watch_rule.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
