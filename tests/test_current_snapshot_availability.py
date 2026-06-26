from __future__ import annotations

import subprocess
import sys

from business_cycle.current.current_snapshot_availability import (
    build_current_snapshot_availability,
    summarize_current_snapshot_availability,
)
from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
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


def test_current_snapshot_availability_accepts_phase40_refresh_manifest() -> None:
    manifest = build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )
    availability = build_current_snapshot_availability(refresh_manifest=manifest)

    assert availability["phase"] == "40"
    assert availability["data_mode"] == "revised_metadata_fixture"
    assert availability["refresh_manifest_artifact_count"] == 1
    assert availability["live_fetch_attempted"] is False
    assert availability["live_fetch_skipped_reason"] == "live_fetch_disabled_by_cli"
    assert availability["refresh_mode"] == "fixture"
    assert availability["fixture_used"] is True
    assert availability["raw_data_committed_count"] == 0
