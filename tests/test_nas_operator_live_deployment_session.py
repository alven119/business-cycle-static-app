from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.service.nas_operator_live_deployment_session import (
    build_nas_operator_live_deployment_session,
    load_nas_operator_live_deployment_session_contract,
    summarize_nas_operator_live_deployment_session,
    validate_operator_live_session_report,
    write_nas_operator_live_deployment_session_report,
)

pytestmark = pytest.mark.archive_regression


def test_nas_operator_live_deployment_session_summary_passes() -> None:
    summary = summarize_nas_operator_live_deployment_session()

    assert summary["result"] == "passed"
    assert summary["nas_operator_live_session_protocol_ready"] is True
    assert summary["phase105_handoff_dependency_ready"] is True
    assert summary["nas_private_ip"] == "192.168.1.116"
    assert summary["operator_must_execute_live_steps_out_of_band"] is True
    assert summary["automatic_live_execution_allowed_now"] is False
    assert summary["required_operator_action_count"] == 41
    assert summary["operator_action_auto_execution_count"] == 0
    assert summary["live_deployment_acceptance_status"] == "operator_report_required"
    assert summary["live_deployment_complete"] is False


def test_nas_operator_live_deployment_session_is_non_executing() -> None:
    session = build_nas_operator_live_deployment_session()

    assert session["session_stage_count"] == 6
    assert session["required_operator_action_count"] == 41
    assert all(
        action["owner"] == "operator" for action in session["action_register"]
    )
    assert all(
        action["automatic_execution_allowed_now"] is False
        for action in session["action_register"]
    )
    assert session["dsm_login_attempt_count"] == 0
    assert session["container_manager_import_attempt_count"] == 0
    assert session["live_db_connection_attempt_count"] == 0
    assert session["postgres_write_attempt_count"] == 0
    assert session["prohibited_output_field_count"] == 0
    assert session["secret_value_literal_count"] == 0


def test_sample_operator_report_validates() -> None:
    session = build_nas_operator_live_deployment_session()
    contract = load_nas_operator_live_deployment_session_contract()
    validation = validate_operator_live_session_report(
        session["sample_operator_report"],
        contract,
    )

    assert validation["operator_report_valid"] is True
    assert validation["operator_report_action_count"] == 41
    assert validation["operator_report_passed_action_count"] == 41
    assert validation["live_deployment_acceptance_status"] == "accepted"
    assert validation["live_deployment_complete"] is True


def test_bad_operator_report_rejects_prohibited_fields() -> None:
    session = build_nas_operator_live_deployment_session()
    contract = load_nas_operator_live_deployment_session_contract()
    bad_report = dict(session["sample_operator_report"])
    bad_report["current_phase"] = "boom"
    validation = validate_operator_live_session_report(bad_report, contract)

    assert validation["operator_report_valid"] is False
    assert validation["operator_report_prohibited_field_count"] == 1
    assert validation["live_deployment_acceptance_status"] == "blocked"


def test_nas_operator_live_deployment_session_writes_only_tmp(
    tmp_path: Path,
) -> None:
    result = write_nas_operator_live_deployment_session_report(tmp_path)

    assert result["result"] == "passed"
    assert result["session_output_path_count"] == 7
    assert result["session_output_under_tmp_only"] is True
    assert result["repo_output_written_count"] == 0
    for path in result["written_paths"]:
        assert Path(path).is_file()
        assert str(path).startswith("/tmp/")


def test_nas_operator_live_deployment_session_rejects_repo_output() -> None:
    with pytest.raises(ValueError, match="/tmp"):
        write_nas_operator_live_deployment_session_report(
            Path("tmp-phase106-output"),
        )


def test_show_nas_operator_live_deployment_session_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_operator_live_deployment_session.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_operator_live_session_protocol_ready=true" in result.stdout
    assert "nas_private_ip=192.168.1.116" in result.stdout
    assert "automatic_live_execution_allowed_now=false" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_operator_live_deployment_session_script(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_operator_live_deployment_session.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_operator_live_session_protocol_ready=true" in result.stdout
    assert "session_output_path_count=7" in result.stdout
    assert "session_output_under_tmp_only=true" in result.stdout
