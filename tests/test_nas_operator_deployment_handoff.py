from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.service.nas_operator_deployment_handoff import (
    build_nas_operator_deployment_handoff,
    summarize_nas_operator_deployment_handoff,
    write_nas_operator_deployment_handoff_report,
)

pytestmark = pytest.mark.archive_regression


def test_nas_operator_deployment_handoff_summary_passes() -> None:
    summary = summarize_nas_operator_deployment_handoff()

    assert summary["result"] == "passed"
    assert summary["nas_operator_deployment_handoff_ready"] is True
    assert summary["phase100_container_manager_bundle_dependency_ready"] is True
    assert summary["phase101_private_startup_dependency_ready"] is True
    assert summary["phase103_connectivity_dependency_ready"] is True
    assert summary["phase104_revised_import_dependency_ready"] is True
    assert summary["nas_private_ip"] == "192.168.1.116"
    assert summary["operator_approval_required"] is True
    assert summary["live_execution_allowed_now"] is False
    assert summary["handoff_artifact_count"] == 8
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_nas_operator_deployment_handoff_is_non_executing() -> None:
    handoff = build_nas_operator_deployment_handoff()

    assert handoff["operator_preflight_check_count"] == 8
    assert handoff["container_manager_import_step_count"] == 8
    assert handoff["private_auth_acceptance_check_count"] == 5
    assert handoff["health_check_count"] == 6
    assert handoff["backup_rollback_acceptance_check_count"] == 6
    assert handoff["go_no_go_gate_count"] == 8
    assert all(
        row["execution_allowed_now"] is False
        for row in handoff["container_manager_import_handoff"]
    )
    assert handoff["dsm_login_attempt_count"] == 0
    assert handoff["container_manager_import_attempt_count"] == 0
    assert handoff["live_db_connection_attempt_count"] == 0
    assert handoff["postgres_write_attempt_count"] == 0
    assert handoff["prohibited_output_field_count"] == 0
    assert handoff["secret_value_literal_count"] == 0


def test_nas_operator_deployment_handoff_writes_only_tmp(tmp_path: Path) -> None:
    result = write_nas_operator_deployment_handoff_report(tmp_path)

    assert result["result"] == "passed"
    assert result["handoff_output_path_count"] == 8
    assert result["handoff_output_under_tmp_only"] is True
    assert result["repo_output_written_count"] == 0
    for path in result["written_paths"]:
        assert Path(path).is_file()
        assert str(path).startswith("/tmp/")


def test_nas_operator_deployment_handoff_rejects_repo_output() -> None:
    with pytest.raises(ValueError, match="/tmp"):
        write_nas_operator_deployment_handoff_report(
            Path("tmp-phase105-output"),
        )


def test_show_nas_operator_deployment_handoff_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_operator_deployment_handoff.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_operator_deployment_handoff_ready=true" in result.stdout
    assert "nas_private_ip=192.168.1.116" in result.stdout
    assert "live_execution_allowed_now=false" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_operator_deployment_handoff_script(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_operator_deployment_handoff.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_operator_deployment_handoff_ready=true" in result.stdout
    assert "handoff_output_path_count=8" in result.stdout
    assert "handoff_output_under_tmp_only=true" in result.stdout
