from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.shadow_autonomous_blocker_unblock_freeze import (
    summarize_shadow_autonomous_blocker_unblock_freeze,
)


def test_alpha30_autonomous_blocker_unblock_freeze_is_valid() -> None:
    summary = summarize_shadow_autonomous_blocker_unblock_freeze()

    assert summary["autonomous_blocker_unblock_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha30"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha29"
    assert summary["alpha30_freeze_hash_valid"] is True
    assert summary["alpha29_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["post_resolution_blocked_scenario_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_show_shadow_autonomous_blocker_unblock_freeze_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_shadow_autonomous_blocker_unblock_freeze.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "freeze_id=book_faithful_shadow_v2_alpha30" in result.stdout
    assert "autonomous_blocker_unblock_freeze_ready=true" in result.stdout
    assert "alpha30_freeze_hash_valid=true" in result.stdout
