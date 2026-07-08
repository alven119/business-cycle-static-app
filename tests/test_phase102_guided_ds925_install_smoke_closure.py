from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase102_guided_ds925_install_smoke_closure import (
    summarize_phase102_guided_ds925_install_smoke_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase102_guided_ds925_install_smoke_closure_passes() -> None:
    summary = summarize_phase102_guided_ds925_install_smoke_closure()

    assert summary["result"] == "passed"
    assert summary["phase102_closure_ready"] is True
    assert summary["nas_guided_ds925_install_smoke_ready"] is True
    assert summary["guided_install_runbook_ready"] is True
    assert summary["nas_side_readonly_smoke_plan_ready"] is True
    assert summary["readonly_smoke_command_executed_count"] == 0
    assert summary["actual_nas_connection_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["phase102_closure_status"]
        == "closed_guided_ds925_install_and_readonly_smoke_plan_ready_no_live_nas_execution"
    )


def test_show_phase102_guided_ds925_install_smoke_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase102_guided_ds925_install_smoke_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase102_closure_ready=true" in result.stdout
    assert "nas_guided_ds925_install_smoke_ready=true" in result.stdout
    assert "readonly_smoke_command_executed_count=0" in result.stdout
    assert "actual_nas_connection_attempt_count=0" in result.stdout
    assert (
        "phase102_closure_status="
        "closed_guided_ds925_install_and_readonly_smoke_plan_ready_no_live_nas_execution"
    ) in result.stdout
    assert "result=passed" in result.stdout
