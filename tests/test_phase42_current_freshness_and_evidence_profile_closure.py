from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase42_current_freshness_and_evidence_profile_closure import (
    summarize_phase42_current_freshness_and_evidence_profile_closure,
)


def test_phase42_current_freshness_and_evidence_profile_closure() -> None:
    summarize_phase42_current_freshness_and_evidence_profile_closure.cache_clear()
    summary = summarize_phase42_current_freshness_and_evidence_profile_closure()

    assert summary["result"] == "passed"
    assert summary["freshness_semantics_ready"] is True
    assert summary["current_evidence_readiness_ready"] is True
    assert summary["dashboard_current_evidence_profile_ready"] is True
    assert summary["alpha39_freeze_hash_valid"] is True
    assert summary["alpha38_parent_preserved"] is True
    assert summary["development_next_phase"] == 43
    assert summary["phase42_closure_status"] == (
        "closed_current_evidence_profile_dashboard_available_no_current_phase_or_performance"
    )


def test_show_phase42_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase42_current_freshness_and_evidence_profile_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase42_closure_status=closed_current_evidence_profile" in result.stdout
    assert "result=passed" in result.stdout
