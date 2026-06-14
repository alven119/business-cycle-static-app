from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def write_scenario_yaml(path: Path) -> Path:
    path.write_text(
        """
scenarios:
  - scenario_id: global_financial_crisis
    display_name_zh: 金融海嘯
    display_name_en: Global Financial Crisis
    window_start: "2005-01-01"
    window_end: "2010-12-31"
    focus_transition: boom_to_recession_to_recovery
    baseline_phase_id: boom
    expected_focus_zh:
      - 測試
    benchmark_notes_zh: 測試
    data_mode: revised
""",
        encoding="utf-8",
    )
    return path


def attribution_payload() -> dict:
    return {
        "scenario_id": "global_financial_crisis",
        "display_name_zh": "金融海嘯",
        "data_mode": "revised",
        "transition_count": 1,
        "diagnostics": [
            {
                "as_of": "2005-10-31",
                "attribution_quality": "full",
                "phase_score_changes": [{"phase_id": "recession", "delta": 20.0}],
                "top_indicator_score_changes": [
                    {"indicator_id": "initial_jobless_claims", "delta": -30.0}
                ],
            }
        ],
        "plausibility_warnings_linked": [
            {"as_of": "2005-10-31", "kind": "short_phase_segment", "phase_id": "recession"}
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
        "warnings": [],
    }


def test_run_attribution_smoke_script_with_scenario_id(tmp_path: Path) -> None:
    scenario_path = write_scenario_yaml(tmp_path / "scenarios.yaml")
    output_dir = tmp_path / "backtests"
    write_json(output_dir / "global_financial_crisis" / "transition_attribution.json", attribution_payload())
    output_path = tmp_path / "attribution_summary.json"

    completed = run_script(
        "--scenario-path",
        str(scenario_path),
        "--scenario-id",
        "global_financial_crisis",
        "--output-dir",
        str(output_dir),
        "--output",
        str(output_path),
        "--reuse-existing",
    )

    assert completed.returncode == 0, completed.stderr
    assert "scenario_count=1" in completed.stdout
    assert "total_diagnostic_count=1" in completed.stdout
    assert output_path.exists()


def test_run_attribution_smoke_script_custom_output(tmp_path: Path) -> None:
    scenario_path = write_scenario_yaml(tmp_path / "scenarios.yaml")
    output_dir = tmp_path / "backtests"
    write_json(output_dir / "global_financial_crisis" / "transition_attribution.json", attribution_payload())
    output_path = tmp_path / "custom" / "summary.json"

    completed = run_script(
        "--scenario-path",
        str(scenario_path),
        "--scenario-id",
        "global_financial_crisis",
        "--output-dir",
        str(output_dir),
        "--output",
        str(output_path),
        "--reuse-existing",
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["output_path"] == str(output_path)
    assert payload["scenarios"][0]["scenario_id"] == "global_financial_crisis"


def test_run_attribution_smoke_reuse_existing_records_missing_outputs(tmp_path: Path) -> None:
    scenario_path = write_scenario_yaml(tmp_path / "scenarios.yaml")
    output_path = tmp_path / "summary.json"

    completed = run_script(
        "--scenario-path",
        str(scenario_path),
        "--scenario-id",
        "global_financial_crisis",
        "--output-dir",
        str(tmp_path / "backtests"),
        "--output",
        str(output_path),
        "--reuse-existing",
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert completed.returncode != 0
    assert payload["aggregate"]["scenario_with_failures_count"] == 1
    assert payload["scenarios"][0]["scenario_failure"]["error_type"] == "FileNotFoundError"


def test_run_attribution_smoke_unknown_scenario_fails(tmp_path: Path) -> None:
    scenario_path = write_scenario_yaml(tmp_path / "scenarios.yaml")
    completed = run_script(
        "--scenario-path",
        str(scenario_path),
        "--scenario-id",
        "missing",
        "--output-dir",
        str(tmp_path / "backtests"),
        "--output",
        str(tmp_path / "summary.json"),
        "--reuse-existing",
    )

    assert completed.returncode != 0
    assert "Unknown scenario_id: missing" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/run_attribution_smoke.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
