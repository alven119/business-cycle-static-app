from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.shadow_current_data_refresh_freeze import (
    summarize_shadow_current_data_refresh_freeze,
)


def test_shadow_current_data_refresh_freeze_passes() -> None:
    summary = summarize_shadow_current_data_refresh_freeze()

    assert summary["current_data_refresh_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha37"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha36"
    assert summary["alpha37_freeze_hash_valid"] is True
    assert summary["alpha36_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_show_shadow_current_data_refresh_freeze_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_shadow_current_data_refresh_freeze.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "current_data_refresh_freeze_ready=true" in result.stdout
    assert "alpha37_freeze_hash_valid=true" in result.stdout
