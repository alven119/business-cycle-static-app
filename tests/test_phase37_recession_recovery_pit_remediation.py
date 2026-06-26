from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase37_recession_recovery_pit_remediation import (
    summarize_phase37_recession_recovery_pit_remediation,
)


def test_phase37_recession_recovery_pit_remediation_audit_passes() -> None:
    summary = summarize_phase37_recession_recovery_pit_remediation()

    assert summary["result"] == "passed"
    assert summary["recession_recovery_pit_gap_matrix_ready"] is True
    assert summary["recession_recovery_pit_remediation_runtime_ready"] is True
    assert summary["controlled_pit_backfill_ready"] is True
    assert summary["post_pit_remediation_validation_rerun_ready"] is True
    assert summary["post_insufficient_point_in_time_role_gap_count"] == 6
    assert summary["phase37_clean_environment_deterministic"] is True
    assert summary["scenario_role_gap_row_count_fields_separated"] is True
    assert summary["safe_fixable_pit_gap_count"] == 0
    assert summary["false_comparability_count"] == 0
    assert summary["development_next_phase"] == 38


def test_show_phase37_recession_recovery_pit_remediation_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase37_recession_recovery_pit_remediation.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "recession_recovery_pit_remediation_runtime_ready=true" in result.stdout
    assert "phase37_progress_status=pit_gaps_reduced_but_comparability_still_limited" in (
        result.stdout
    )
    assert "result=passed" in result.stdout
