from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def timeline() -> dict:
    return {
        "scenario_id": "global_financial_crisis",
        "display_name_zh": "金融海嘯",
        "data_mode": "revised",
        "periods": [
            {
                "as_of": "2020-01-31",
                "current_phase_id": "boom",
                "decision_status": "hold_current",
                "candidate_phase_id": "recession",
                "confidence": 0.7,
                "phase_scores": [{"phase_id": "recession", "score": 40.0}],
                "warnings": [],
                "failures": [],
            },
            {
                "as_of": "2020-02-29",
                "current_phase_id": "recession",
                "decision_status": "confirmed",
                "candidate_phase_id": "recession",
                "confidence": 0.8,
                "phase_scores": [{"phase_id": "recession", "score": 65.0}],
                "warnings": [],
                "failures": [],
            },
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }


def report() -> dict:
    return {
        "scenario_id": "global_financial_crisis",
        "display_name_zh": "金融海嘯",
        "data_mode": "revised",
        "transition_events": [
            {
                "as_of": "2020-02-29",
                "from_phase_id": "boom",
                "to_phase_id": "recession",
                "decision_status": "confirmed",
                "candidate_phase_id": "recession",
                "confidence": 0.8,
            }
        ],
        "plausibility_warnings": [],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }


def write_fixture(root: Path) -> tuple[Path, Path, Path]:
    scenario_dir = root / "data" / "backtests" / "global_financial_crisis"
    timeline_path = write_json(scenario_dir / "timeline.json", timeline())
    report_path = write_json(scenario_dir / "report.json", report())
    intermediate_dir = scenario_dir / "intermediate"
    write_json(
        intermediate_dir / "2020-01-31" / "indicator_scores.json",
        {"results": [{"indicator_id": "initial_jobless_claims", "score": 20.0}]},
    )
    write_json(
        intermediate_dir / "2020-02-29" / "indicator_scores.json",
        {"results": [{"indicator_id": "initial_jobless_claims", "score": 80.0}]},
    )
    write_json(
        intermediate_dir / "2020-02-29" / "phase_scores.json",
        {
            "results": [
                {
                    "phase_id": "recession",
                    "contributing_indicators": [
                        {"indicator_id": "initial_jobless_claims", "weighted_contribution": 20.0}
                    ],
                }
            ]
        },
    )
    return timeline_path, report_path, intermediate_dir


def test_diagnose_script_with_scenario_id_writes_default_output(tmp_path: Path) -> None:
    write_fixture(tmp_path)

    completed = run_script("--scenario-id", "global_financial_crisis", cwd=tmp_path)

    output_path = tmp_path / "data" / "backtests" / "global_financial_crisis" / "transition_attribution.json"
    assert completed.returncode == 0, completed.stderr
    assert "scenario_id=global_financial_crisis" in completed.stdout
    assert "transition_count=1" in completed.stdout
    assert output_path.exists()


def test_diagnose_script_with_custom_paths(tmp_path: Path) -> None:
    timeline_path, report_path, intermediate_dir = write_fixture(tmp_path)
    output_path = tmp_path / "custom_attribution.json"

    completed = run_script(
        "--timeline",
        str(timeline_path),
        "--report",
        str(report_path),
        "--intermediate-dir",
        str(intermediate_dir),
        "--output",
        str(output_path),
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["transition_count"] == 1
    assert payload["diagnostics"][0]["top_indicator_score_changes"][0]["delta"] == 60.0


def test_diagnose_script_missing_inputs_fails(tmp_path: Path) -> None:
    completed = run_script(
        "--timeline",
        str(tmp_path / "missing_timeline.json"),
        "--report",
        str(tmp_path / "missing_report.json"),
    )

    assert completed.returncode != 0
    assert "Run scripts/run_backtest.py and scripts/summarize_backtest.py first" in completed.stderr


def test_diagnose_script_requires_input() -> None:
    completed = run_script()

    assert completed.returncode != 0
    assert "provide --scenario-id or both --timeline and --report" in completed.stderr


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    script_path = project_root / "scripts" / "diagnose_backtest_transitions.py"
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=cwd or project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
