from __future__ import annotations

import os
import subprocess
import sys

from business_cycle.audits.shadow_live_current_refresh_smoke_freeze import (
    summarize_shadow_live_current_refresh_smoke_freeze,
)


def test_alpha38_live_current_refresh_smoke_freeze(monkeypatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    summarize_shadow_live_current_refresh_smoke_freeze.cache_clear()
    summary = summarize_shadow_live_current_refresh_smoke_freeze()

    assert summary["live_current_refresh_smoke_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha38"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha37"
    assert summary["alpha38_freeze_hash_valid"] is True
    assert summary["alpha37_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_show_alpha38_freeze_script(monkeypatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    result = subprocess.run(
        [sys.executable, "scripts/show_shadow_live_current_refresh_smoke_freeze.py"],
        check=True,
        capture_output=True,
        env={**os.environ, "FRED_API_KEY": ""},
        text=True,
    )

    assert "live_current_refresh_smoke_freeze_ready=true" in result.stdout
    assert "alpha38_freeze_hash_valid=true" in result.stdout
