from __future__ import annotations

import os
import subprocess
import sys

from business_cycle.audits.phase41_live_current_refresh_smoke_closure import (
    summarize_phase41_live_current_refresh_smoke_closure,
)


def test_phase41_live_current_refresh_smoke_closure(monkeypatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    summarize_phase41_live_current_refresh_smoke_closure.cache_clear()
    summary = summarize_phase41_live_current_refresh_smoke_closure()

    assert summary["result"] == "passed"
    assert summary["phase_id"] == 41
    assert summary["north_star_alignment_status"] == "aligned"
    assert summary["semantic_drift_count"] == 0
    assert summary["live_fetch_blocked_reason"] == "missing_fred_api_key"
    assert summary["phase41_live_refresh_status"] == "blocked_missing_local_secret"
    assert summary["alpha38_freeze_hash_valid"] is True
    assert summary["alpha37_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["economic_validation_status"] == (
        "live_current_refresh_smoke_exercised_or_safely_blocked_no_current_phase"
    )
    assert summary["development_next_phase"] == 42
    assert summary["phase41_closure_status"] == (
        "closed_live_current_refresh_smoke_exercised_or_safely_blocked_no_current_phase"
    )


def test_show_phase41_live_current_refresh_smoke_closure_script(monkeypatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    result = subprocess.run(
        [sys.executable, "scripts/show_phase41_live_current_refresh_smoke_closure.py"],
        check=True,
        capture_output=True,
        env={**os.environ, "FRED_API_KEY": ""},
        text=True,
    )

    assert "phase41_closure_status=closed_live_current_refresh_smoke" in result.stdout
    assert "live_fetch_blocked_reason=missing_fred_api_key" in result.stdout
    assert "result=passed" in result.stdout
