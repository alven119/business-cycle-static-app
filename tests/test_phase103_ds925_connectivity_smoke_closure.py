from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase103_ds925_connectivity_smoke_closure import (
    summarize_phase103_ds925_connectivity_smoke_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase103_ds925_connectivity_smoke_closure_passes() -> None:
    summary = summarize_phase103_ds925_connectivity_smoke_closure()

    assert summary["result"] == "passed"
    assert summary["phase103_closure_ready"] is True
    assert summary["nas_private_ip"] == "192.168.1.116"
    assert summary["nas_private_ip_private_lan"] is True
    assert summary["default_probe_execution_count"] == 0
    assert summary["tests_network_dependency_count"] == 0
    assert summary["dsm_login_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["phase103_closure_status"]
        == "closed_ds925_private_lan_connectivity_smoke_ready_no_auth_or_db_write"
    )


def test_show_phase103_ds925_connectivity_smoke_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase103_ds925_connectivity_smoke_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase103_closure_ready=true" in result.stdout
    assert "nas_ds925_connectivity_smoke_ready=true" in result.stdout
    assert "nas_private_ip=192.168.1.116" in result.stdout
    assert "default_probe_execution_count=0" in result.stdout
    assert "dsm_login_attempt_count=0" in result.stdout
    assert (
        "phase103_closure_status="
        "closed_ds925_private_lan_connectivity_smoke_ready_no_auth_or_db_write"
    ) in result.stdout
    assert "result=passed" in result.stdout
