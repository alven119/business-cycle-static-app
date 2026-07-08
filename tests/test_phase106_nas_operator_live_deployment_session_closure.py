from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase106_nas_operator_live_deployment_session_closure import (
    summarize_phase106_nas_operator_live_deployment_session_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase106_nas_operator_live_deployment_session_closure_passes() -> None:
    summary = summarize_phase106_nas_operator_live_deployment_session_closure()

    assert summary["result"] == "passed"
    assert summary["phase106_closure_ready"] is True
    assert summary["nas_operator_live_session_protocol_ready"] is True
    assert summary["phase105_handoff_dependency_ready"] is True
    assert summary["required_operator_action_count"] == 41
    assert summary["automatic_live_execution_allowed_now"] is False
    assert summary["live_deployment_acceptance_status"] == "operator_report_required"
    assert summary["live_deployment_complete"] is False
    assert summary["development_next_phase"] == 107
    assert (
        summary["phase106_closure_status"]
        == "closed_nas_operator_live_session_protocol_ready_operator_report_required"
    )


def test_show_phase106_nas_operator_live_deployment_session_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase106_nas_operator_live_deployment_session_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase106_closure_ready=true" in result.stdout
    assert "nas_operator_live_session_protocol_ready=true" in result.stdout
    assert "required_operator_action_count=41" in result.stdout
    assert (
        "phase106_closure_status="
        "closed_nas_operator_live_session_protocol_ready_operator_report_required"
    ) in result.stdout
