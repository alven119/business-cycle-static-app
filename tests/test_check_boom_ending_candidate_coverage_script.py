from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_check_boom_ending_candidate_coverage_outputs_summary() -> None:
    completed = run_script()

    assert completed.returncode == 0, completed.stderr
    assert "candidate_indicator_count=8" in completed.stdout
    assert "required_series_count=12" in completed.stdout
    assert "available_series_count=" in completed.stdout
    assert "notes=local cache check only; no FRED API calls were made" in completed.stdout


def test_check_boom_ending_candidate_coverage_counts_fake_cache(tmp_path: Path) -> None:
    cache_dir = tmp_path / "fred"
    cache_dir.mkdir()
    write_csv(cache_dir / "T10Y3M.csv")
    write_csv(cache_dir / "BAA.csv")

    completed = run_script("--cache-dir", str(cache_dir))

    assert completed.returncode == 0, completed.stderr
    assert "available_series_count=2" in completed.stdout
    assert "cached_series=BAA,T10Y3M" in completed.stdout


def test_check_boom_ending_candidate_coverage_missing_cache_does_not_crash(
    tmp_path: Path,
) -> None:
    completed = run_script("--cache-dir", str(tmp_path / "missing"))

    assert completed.returncode == 0, completed.stderr
    assert "available_series_count=0" in completed.stdout


def write_csv(path: Path) -> None:
    path.write_text("date,value\n2024-01-01,1.0\n", encoding="utf-8")


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/check_boom_ending_candidate_coverage.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
