from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase105_nas_operator_deployment_handoff_closure import (
    summarize_phase105_nas_operator_deployment_handoff_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase105_nas_operator_deployment_handoff_closure_passes() -> None:
    summary = summarize_phase105_nas_operator_deployment_handoff_closure()

    assert summary["result"] == "passed"
    assert summary["phase105_closure_ready"] is True
    assert summary["nas_operator_deployment_handoff_ready"] is True
    assert summary["phase104_revised_import_dependency_ready"] is True
    assert summary["nas_private_ip"] == "192.168.1.116"
    assert summary["handoff_artifact_count"] == 8
    assert summary["container_manager_import_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["development_next_phase"] == 106
    assert (
        summary["phase105_closure_status"]
        == "closed_nas_operator_deployment_handoff_ready_no_live_execution"
    )


def test_show_phase105_nas_operator_deployment_handoff_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase105_nas_operator_deployment_handoff_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase105_closure_ready=true" in result.stdout
    assert "nas_operator_deployment_handoff_ready=true" in result.stdout
    assert "handoff_artifact_count=8" in result.stdout
    assert (
        "phase105_closure_status="
        "closed_nas_operator_deployment_handoff_ready_no_live_execution"
    ) in result.stdout
