from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase38_research_validation_dashboard import (
    summarize_phase38_research_validation_dashboard,
)


def test_phase38_research_validation_dashboard_audit_passes() -> None:
    summary = summarize_phase38_research_validation_dashboard()

    assert summary["result"] == "passed"
    assert summary["research_dashboard_contract_ready"] is True
    assert summary["research_dashboard_bundle_ready"] is True
    assert summary["research_dashboard_runtime_ready"] is True
    assert summary["browser_verification_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["rendered_scenario_count"] == 5
    assert summary["comparable_scenario_count"] == 2
    assert summary["non_comparable_scenario_count"] == 3
    assert summary["artifact_consistency_error_count"] == 0
    assert summary["prohibited_claim_count"] == 0
    assert summary["prohibited_action_field_count"] == 0
    assert summary["development_next_phase"] == 39


def test_show_phase38_research_validation_dashboard_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase38_research_validation_dashboard.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "research_dashboard_runtime_ready=true" in result.stdout
    assert "browser_verification_ready=true" in result.stdout
    assert "result=passed" in result.stdout
