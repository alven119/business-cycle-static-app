from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase99_nas_postgres_readonly_smoke_closure import (
    summarize_phase99_nas_postgres_readonly_smoke_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase99_nas_postgres_readonly_smoke_closure_passes() -> None:
    summary = summarize_phase99_nas_postgres_readonly_smoke_closure()

    assert summary["result"] == "passed"
    assert summary["phase99_closure_ready"] is True
    assert summary["nas_postgres_readonly_smoke_ready"] is True
    assert summary["readonly_query_pass_count"] == 4
    assert summary["readonly_result_row_count"] == 16
    assert summary["forbidden_sql_rejected_count"] == 12
    assert summary["forbidden_sql_accepted_count"] == 0
    assert summary["live_db_connection_attempt_count"] == 0
    assert summary["postgres_read_attempt_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["nas_ds925_package_assessment_ready"] is True
    assert summary["primary_runtime_recommended"] == "synology_container_manager"
    assert summary["private_mobile_access_recommended"] == "tailscale"
    assert summary["recommended_guided_ds925_deploy_phase"] == 102
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert (
        summary["phase99_closure_status"]
        == "closed_nas_postgres_readonly_fixture_smoke_ready_"
        "ds925_package_path_assessed"
    )


def test_show_phase99_nas_postgres_readonly_smoke_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase99_nas_postgres_readonly_smoke_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase99_closure_ready=true" in result.stdout
    assert "nas_postgres_readonly_smoke_ready=true" in result.stdout
    assert "readonly_query_pass_count=4" in result.stdout
    assert "nas_ds925_package_assessment_ready=true" in result.stdout
    assert (
        "phase99_closure_status="
        "closed_nas_postgres_readonly_fixture_smoke_ready_"
        "ds925_package_path_assessed"
    ) in result.stdout
    assert "result=passed" in result.stdout
