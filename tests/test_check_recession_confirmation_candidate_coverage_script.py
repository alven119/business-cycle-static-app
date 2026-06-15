from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_check_recession_confirmation_candidate_coverage_outputs_summary(tmp_path: Path) -> None:
    cache_dir = tmp_path / "raw" / "fred"
    cache_dir.mkdir(parents=True)
    (cache_dir / "CCSA.csv").write_text("series_id,date,value\nCCSA,2020-01-01,1\n", encoding="utf-8")

    completed = run_script("--cache-dir", str(cache_dir))

    assert completed.returncode == 0, completed.stderr
    assert "candidate_indicator_count=7" in completed.stdout
    assert "required_series_count=" in completed.stdout
    assert "available_series_count=1" in completed.stdout
    assert "missing_series=" in completed.stdout
    assert "derived_series=credit_spread_baa_aaa" in completed.stdout
    assert "no FRED API calls" in completed.stdout


def test_check_recession_confirmation_candidate_coverage_missing_cache_does_not_crash(tmp_path: Path) -> None:
    completed = run_script("--cache-dir", str(tmp_path / "missing"))

    assert completed.returncode == 0, completed.stderr
    assert "available_series_count=0" in completed.stdout


def test_check_recession_confirmation_candidate_coverage_missing_spec_fails(tmp_path: Path) -> None:
    completed = run_script("--spec", str(tmp_path / "missing.yaml"))

    assert completed.returncode != 0
    assert "Candidate indicator spec file does not exist" in completed.stderr


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/check_recession_confirmation_candidate_coverage.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
