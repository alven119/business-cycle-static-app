from __future__ import annotations

import os
import subprocess
import sys

from business_cycle.audits.phase41_live_current_refresh_smoke import (
    summarize_phase41_live_current_refresh_smoke,
)


def test_phase41_live_current_refresh_smoke_passes_without_key(monkeypatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    summarize_phase41_live_current_refresh_smoke.cache_clear()
    summary = summarize_phase41_live_current_refresh_smoke()

    assert summary["result"] == "passed"
    assert summary["live_refresh_probe_ready"] is True
    assert summary["controlled_live_refresh_smoke_ready"] is True
    assert summary["live_fetch_attempted"] is False
    assert summary["live_fetch_blocked_reason"] == "missing_fred_api_key"
    assert summary["phase41_live_refresh_status"] == "blocked_missing_local_secret"
    assert summary["dashboard_browser_verification_passed"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_show_phase41_live_current_refresh_smoke_script(monkeypatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    result = subprocess.run(
        [sys.executable, "scripts/show_phase41_live_current_refresh_smoke.py"],
        check=True,
        capture_output=True,
        env={**os.environ, "FRED_API_KEY": ""},
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "live_fetch_blocked_reason=missing_fred_api_key" in result.stdout
    assert "phase41_live_refresh_status=blocked_missing_local_secret" in result.stdout
