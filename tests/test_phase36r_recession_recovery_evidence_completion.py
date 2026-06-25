from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase36r_recession_recovery_evidence_completion import (
    summarize_phase36r_recession_recovery_evidence_completion,
)


def test_phase36r_recession_recovery_evidence_completion_audit_passes() -> None:
    summary = summarize_phase36r_recession_recovery_evidence_completion()

    assert summary["result"] == "passed"
    assert summary["recession_recovery_evidence_completion_runtime_ready"] is True
    assert summary["post_evidence_completion_validation_rerun_ready"] is True
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["safe_fixable_recession_recovery_gap_count"] == 0
    assert summary["unresolved_safe_fixable_recession_recovery_gap_count"] == 0
    assert summary["false_comparability_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["economic_performance_metric_count"] == 0


def test_show_phase36r_recession_recovery_evidence_completion_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase36r_recession_recovery_evidence_completion.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase36r_progress_status=" in result.stdout
    assert "result=passed" in result.stdout
