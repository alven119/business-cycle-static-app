from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import scripts.update_recovery_candidate_data as update_script
from business_cycle.data_sources import SeriesObservation


class FakeProvider:
    def __init__(self) -> None:
        self.downloaded: list[str] = []

    def fetch_series_observations(self, series_id: str) -> list[SeriesObservation]:
        self.downloaded.append(series_id)
        return [SeriesObservation(series_id=series_id, date="2024-01-01", value="1.0")]


def test_update_recovery_candidate_data_dry_run_succeeds_without_api_key(tmp_path: Path) -> None:
    completed = run_script("--dry-run", "--raw-dir", str(tmp_path / "raw"))

    assert completed.returncode == 0, completed.stderr
    assert "required_series_count=16" in completed.stdout
    assert "downloaded_series_count=0" in completed.stdout
    assert "FRED_API_KEY" not in completed.stdout


def test_update_recovery_candidate_data_no_api_succeeds_without_api_key(tmp_path: Path) -> None:
    completed = run_script("--no-api", "--raw-dir", str(tmp_path / "raw"))

    assert completed.returncode == 0, completed.stderr
    assert "required_series_count=16" in completed.stdout
    assert "notes=no_api" in completed.stdout


def test_update_recovery_candidate_data_missing_api_key_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(update_script, "load_dotenv", lambda: None)
    monkeypatch.delenv("FRED_API_KEY", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        update_script.main(["--raw-dir", str(tmp_path / "raw")])

    stderr = capsys.readouterr().err
    assert exc_info.value.code == 1
    assert "FRED_API_KEY is not set" in stderr
    assert "FRED_API_KEY" + "=" not in stderr


def test_update_recovery_candidate_data_main_can_use_fake_provider(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    spec_path = write_spec(tmp_path)
    fake_provider = FakeProvider()
    original_update = update_script.update_candidate_fred_cache

    def fake_update(**kwargs):  # type: ignore[no-untyped-def]
        kwargs["provider"] = fake_provider
        return original_update(**kwargs)

    monkeypatch.setattr(update_script, "load_dotenv", lambda: None)
    monkeypatch.setenv("FRED_API_KEY", "test-key-not-printed")
    monkeypatch.setattr(update_script, "update_candidate_fred_cache", fake_update)

    exit_code = update_script.main(["--spec", str(spec_path), "--raw-dir", str(tmp_path / "raw")])

    stdout = capsys.readouterr().out
    assert exit_code == 0
    assert "downloaded_series_count=1" in stdout
    assert "test-key-not-printed" not in stdout


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


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "scripts/update_recovery_candidate_data.py", *args],
        cwd=project_root,
        env={"PATH": ""},
        check=False,
        capture_output=True,
        text=True,
    )
