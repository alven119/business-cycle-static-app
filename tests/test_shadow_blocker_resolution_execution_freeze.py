from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.shadow_blocker_resolution_execution_freeze import (
    summarize_shadow_blocker_resolution_execution_freeze,
)


def test_alpha29_blocker_resolution_execution_freeze_is_valid() -> None:
    summary = summarize_shadow_blocker_resolution_execution_freeze()

    assert summary["blocker_resolution_execution_freeze_ready"] is True
    assert summary["freeze_id"] == "book_faithful_shadow_v2_alpha29"
    assert summary["parent_freeze_id"] == "book_faithful_shadow_v2_alpha28"
    assert summary["alpha29_freeze_hash_valid"] is True
    assert summary["alpha28_parent_preserved"] is True
    assert summary["qa12_freeze_unchanged"] is True
    assert summary["missing_file_count"] == 0
    assert summary["hash_mismatch_count"] == 0
    assert summary["secret_count"] == 0
    assert summary["production_file_count"] == 0
    assert summary["work_package_count"] == 5
    assert summary["executed_work_package_count"] == 5
    assert summary["still_genuine_blocked_work_package_count"] == 5
    assert summary["false_resolution_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["economic_validation_status"] == (
        "blocker_resolution_execution_research_only_no_performance"
    )


def test_show_shadow_blocker_resolution_execution_freeze_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_shadow_blocker_resolution_execution_freeze.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "blocker_resolution_execution_freeze_ready=true" in result.stdout
    assert "freeze_id=book_faithful_shadow_v2_alpha29" in result.stdout
