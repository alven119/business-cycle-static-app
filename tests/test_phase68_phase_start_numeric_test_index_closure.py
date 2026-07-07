from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase68_phase_start_numeric_test_index_closure import (
    summarize_phase68_phase_start_numeric_test_index_closure,
)


def test_phase68_phase_start_numeric_test_index_closure_passes() -> None:
    summary = summarize_phase68_phase_start_numeric_test_index_closure()

    assert summary["result"] == "passed"
    assert summary["phase68_phase_start_numeric_test_index_ready"] is True
    assert summary["declared_boom_start_governance_ready"] is True
    assert summary["user_confirmation_required"] is True
    assert summary["registry_write_allowed"] is False
    assert summary["declared_registry_modified"] is False
    assert summary["phase_age_false_precision_count"] == 0
    assert summary["numeric_cache_overlay_supported"] is True
    assert summary["actual_numeric_cache_fixture_role_count"] > 0
    assert summary["lane_with_actual_numeric_context_fixture_count"] > 0
    assert summary["test_suite_index_ready"] is True
    assert summary["default_product_core_test_file_count"] == 29
    assert summary["duplicate_test_guard_key_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_show_phase68_phase_start_numeric_test_index_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase68_phase_start_numeric_test_index_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase68_phase_start_numeric_test_index_ready=true" in completed.stdout
    assert "numeric_cache_overlay_supported=true" in completed.stdout
    assert "test_suite_index_ready=true" in completed.stdout
    assert "default_product_core_test_file_count=29" in completed.stdout
    assert "result=passed" in completed.stdout
