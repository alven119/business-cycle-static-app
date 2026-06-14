from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def timeline() -> dict:
    return {
        "scenario_id": "global_financial_crisis",
        "display_name_zh": "金融海嘯",
        "window_start": "2005-01-01",
        "window_end": "2005-02-28",
        "data_mode": "revised",
        "periods": [
            {
                "as_of": "2005-01-31",
                "current_phase_id": "boom",
                "decision_status": "hold_current",
                "candidate_phase_id": "recession",
                "confidence": 0.7,
                "phase_scores": [
                    {
                        "phase_id": "boom",
                        "score": 70,
                        "confidence": 0.8,
                        "available_weight": 1.0,
                        "stage_hint": None,
                    }
                ],
                "warnings": [],
                "failures": [],
            },
            {
                "as_of": "2005-02-28",
                "current_phase_id": "recession",
                "decision_status": "confirmed",
                "candidate_phase_id": "recession",
                "confidence": 0.75,
                "phase_scores": [
                    {
                        "phase_id": "recession",
                        "score": 80,
                        "confidence": 0.8,
                        "available_weight": 1.0,
                        "stage_hint": None,
                    }
                ],
                "warnings": [],
                "failures": [],
            }
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }


def test_summarize_backtest_with_scenario_id_default_path(tmp_path: Path) -> None:
    timeline_path = tmp_path / "data" / "backtests" / "global_financial_crisis" / "timeline.json"
    timeline_path.parent.mkdir(parents=True)
    timeline_path.write_text(json.dumps(timeline(), ensure_ascii=False), encoding="utf-8")

    completed = run_script(
        "--scenario-id",
        "global_financial_crisis",
        cwd=tmp_path,
    )

    report_path = timeline_path.with_name("report.json")
    assert completed.returncode == 0, completed.stderr
    assert "scenario_id=global_financial_crisis" in completed.stdout
    assert "plausibility_warning_count=" in completed.stdout
    assert "plausibility_warning kind=" in completed.stdout
    assert report_path.exists()


def test_summarize_backtest_with_custom_timeline_and_output(tmp_path: Path) -> None:
    timeline_path = tmp_path / "timeline.json"
    output_path = tmp_path / "custom_report.json"
    timeline_path.write_text(json.dumps(timeline(), ensure_ascii=False), encoding="utf-8")

    completed = run_script(
        "--timeline",
        str(timeline_path),
        "--output",
        str(output_path),
    )

    assert completed.returncode == 0, completed.stderr
    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8"))["period_count"] == 2


def test_summarize_backtest_missing_timeline_fails(tmp_path: Path) -> None:
    completed = run_script("--timeline", str(tmp_path / "missing.json"))

    assert completed.returncode != 0
    assert "Run scripts/run_backtest.py first" in completed.stderr


def test_summarize_backtest_requires_input() -> None:
    completed = run_script()

    assert completed.returncode != 0
    assert "provide --scenario-id or --timeline" in completed.stderr


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    script_path = project_root / "scripts" / "summarize_backtest.py"
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=cwd or project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
