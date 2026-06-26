from __future__ import annotations

import subprocess
import sys

from business_cycle.current.current_snapshot_availability import (
    summarize_current_snapshot_availability,
)


def test_current_snapshot_availability_is_fixture_based_no_network() -> None:
    summary = summarize_current_snapshot_availability()

    assert summary["current_snapshot_availability_ready"] is True
    assert summary["snapshot_as_of"]
    assert summary["requested_series_count"] > 0
    assert summary["available_series_count"] > 0
    assert summary["live_fetch_attempted"] is False
    assert summary["live_fetch_succeeded"] is False
    assert summary["cache_used"] is False
    assert summary["fixture_used"] is True
    assert summary["secret_logged_count"] == 0
    assert summary["raw_data_committed_count"] == 0


def test_show_current_snapshot_availability_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_current_snapshot_availability.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "current_snapshot_availability_ready=true" in result.stdout
    assert "live_fetch_attempted=false" in result.stdout
