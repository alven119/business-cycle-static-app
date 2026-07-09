from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase108_nas_container_manager_live_start_closure import (
    summarize_phase108_nas_container_manager_live_start_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase108_nas_container_manager_live_start_closure_passes() -> None:
    summary = summarize_phase108_nas_container_manager_live_start_closure()

    assert summary["result"] == "passed"
    assert summary["phase108_closure_ready"] is True
    assert summary["nas_container_manager_live_start_package_ready"] is True
    assert summary["app_image_reference"] == "business-cycle-nas-app:phase107"
    assert summary["live_start_acceptance_status"] == "operator_report_required"
    assert summary["live_deployment_complete"] is False
    assert summary["codex_container_start_attempt_count"] == 0
    assert summary["phase108_closure_status"] == (
        "closed_nas_container_manager_live_start_package_ready_waiting_operator_report"
    )


def test_show_phase108_nas_container_manager_live_start_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase108_nas_container_manager_live_start_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase108_closure_ready=true" in result.stdout
    assert "nas_container_manager_live_start_package_ready=true" in result.stdout
    assert "live_start_acceptance_status=operator_report_required" in result.stdout
    assert (
        "phase108_closure_status="
        "closed_nas_container_manager_live_start_package_ready_waiting_operator_report"
        in result.stdout
    )
