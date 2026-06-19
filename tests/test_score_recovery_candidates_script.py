from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_score_recovery_candidates_script_with_fake_cache(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path)
    cache_dir = tmp_path / "fred"
    cache_dir.mkdir()
    write_series(cache_dir / "ICSA.csv", [220.0] * 40 + [520.0] * 8 + [500.0, 460.0, 420.0, 380.0])
    output_path = tmp_path / "scores.json"

    completed = run_script(
        "--as-of",
        "2021-01-29",
        "--spec",
        str(spec_path),
        "--cache-dir",
        str(cache_dir),
        "--output",
        str(output_path),
    )

    assert completed.returncode == 0, completed.stderr
    assert "as_of=2021-01-29" in completed.stdout
    assert "total_candidates=1" in completed.stdout
    assert "scored_candidates=1" in completed.stdout
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["scores"][0]["indicator_id"] == "initial_jobless_claims_peak_reversal"
    assert payload["scores"][0]["score"] >= 60


def test_score_recovery_candidates_missing_series_warns_without_crash(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path)
    output_path = tmp_path / "scores.json"

    completed = run_script(
        "--as-of",
        "2021-01-29",
        "--spec",
        str(spec_path),
        "--cache-dir",
        str(tmp_path / "missing"),
        "--output",
        str(output_path),
    )

    assert completed.returncode == 0, completed.stderr
    assert "scored_candidates=0" in completed.stdout
    assert "failed_candidates=1" in completed.stdout
    assert "warnings=1" in completed.stdout
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["failures"][0]["error_type"] == "MissingRawCsv"


def test_score_recovery_candidates_as_of_is_required() -> None:
    completed = run_script()

    assert completed.returncode != 0
    assert "--as-of" in completed.stderr


def write_spec(tmp_path: Path) -> Path:
    path = tmp_path / "recovery_candidates.yaml"
    path.write_text(
        """
recovery_candidate_indicators:
  version: 1
  status: test
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  indicators:
    - indicator_id: initial_jobless_claims_peak_reversal
      display_name_zh: claims
      purpose_group: recession_trough_recovery
      provider: fred
      candidate_fred_series: [ICSA]
      preferred_series: ICSA
      transformation: [moving_average]
      proposed_score_method: peak_reversal_score
      expected_phase_impact: {recovery: support}
      implementation_priority: high
""",
        encoding="utf-8",
    )
    return path


def write_series(path: Path, values: list[float]) -> None:
    rows = ["date,value"]
    for date, value in zip(weeks(len(values)), values, strict=True):
        rows.append(f"{date},{value}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def weeks(count: int) -> list[str]:
    import pandas as pd

    return [item.date().isoformat() for item in pd.date_range("2020-01-03", periods=count, freq="W-FRI")]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/score_recovery_candidates.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
