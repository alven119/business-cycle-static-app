from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase100_container_manager_bundle_closure import (
    summarize_phase100_container_manager_bundle_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase100_container_manager_bundle_closure_passes() -> None:
    summary = summarize_phase100_container_manager_bundle_closure()

    assert summary["result"] == "passed"
    assert summary["phase100_closure_ready"] is True
    assert summary["nas_container_manager_bundle_ready"] is True
    assert summary["compose_yaml_valid"] is True
    assert summary["compose_service_count"] == 3
    assert summary["host_port_publish_count"] == 0
    assert summary["container_manager_import_attempt_count"] == 0
    assert summary["docker_compose_execution_count"] == 0
    assert summary["container_start_attempt_count"] == 0
    assert summary["live_db_connection_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["phase100_closure_status"]
        == "closed_container_manager_bundle_dry_run_ready_no_import_or_live_service"
    )


def test_show_phase100_container_manager_bundle_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase100_container_manager_bundle_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase100_closure_ready=true" in result.stdout
    assert "nas_container_manager_bundle_ready=true" in result.stdout
    assert "compose_yaml_valid=true" in result.stdout
    assert "host_port_publish_count=0" in result.stdout
    assert (
        "phase100_closure_status="
        "closed_container_manager_bundle_dry_run_ready_no_import_or_live_service"
    ) in result.stdout
    assert "result=passed" in result.stdout
