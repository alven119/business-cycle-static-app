from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from business_cycle.service.nas_guided_ds925_install_smoke import (
    build_nas_guided_ds925_install_smoke,
    summarize_nas_guided_ds925_install_smoke,
    write_nas_guided_ds925_install_smoke_report,
)

pytestmark = pytest.mark.archive_regression


def test_nas_guided_ds925_install_smoke_summary_passes() -> None:
    summary = summarize_nas_guided_ds925_install_smoke()

    assert summary["result"] == "passed"
    assert summary["nas_guided_ds925_install_smoke_contract_ready"] is True
    assert summary["nas_guided_ds925_install_smoke_ready"] is True
    assert summary["package_assessment_dependency_ready"] is True
    assert summary["phase101_startup_smoke_dependency_ready"] is True
    assert summary["phase100_bundle_dependency_ready"] is True
    assert summary["phase99_readonly_smoke_dependency_ready"] is True
    assert summary["guided_install_runbook_ready"] is True
    assert summary["nas_side_readonly_smoke_plan_ready"] is True
    assert summary["readonly_smoke_command_executed_count"] == 0
    assert summary["actual_nas_connection_attempt_count"] == 0
    assert summary["container_manager_import_attempt_count"] == 0
    assert summary["container_start_attempt_count"] == 0


def test_nas_guided_ds925_install_smoke_plan_preserves_private_boundaries() -> None:
    smoke = build_nas_guided_ds925_install_smoke()
    runbook = smoke["install_runbook"]
    smoke_plan = smoke["readonly_smoke_plan"]

    assert runbook["public_internet_exposure_default"] is False
    assert runbook["execution_allowed_now"] is False
    assert smoke_plan["command_execution_allowed_now"] is False
    assert smoke_plan["must_not_write_postgres"] is True
    assert smoke_plan["must_not_run_schema_migration"] is True
    assert smoke["frontend_database_access_allowed"] is False
    assert smoke["frontend_api_key_allowed"] is False
    assert smoke["candidate_phase_emitted"] is False
    assert smoke["current_phase_emitted"] is False


def test_nas_guided_ds925_install_smoke_writes_only_tmp(tmp_path: Path) -> None:
    output = write_nas_guided_ds925_install_smoke_report(tmp_path)

    assert output["result"] == "passed"
    assert output["guided_install_output_path_count"] == 3
    assert output["guided_install_output_under_tmp_only"] is True
    assert output["repo_output_written_count"] == 0
    assert output["public_output_count"] == 0
    for path in output["written_paths"]:
        assert Path(path).is_file()
        assert str(path).startswith("/tmp/")


def test_nas_guided_ds925_install_smoke_rejects_repo_output_path() -> None:
    with pytest.raises(ValueError, match="/tmp"):
        write_nas_guided_ds925_install_smoke_report(Path("tmp-phase102-output"))


def test_show_nas_guided_ds925_install_smoke_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_guided_ds925_install_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_guided_ds925_install_smoke_ready=true" in result.stdout
    assert "guided_install_runbook_ready=true" in result.stdout
    assert "nas_side_readonly_smoke_plan_ready=true" in result.stdout
    assert "actual_nas_connection_attempt_count=0" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_guided_ds925_install_smoke_script(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_guided_ds925_install_smoke.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_guided_ds925_install_smoke_ready=true" in result.stdout
    assert "readonly_smoke_command_executed_count=0" in result.stdout
    assert "guided_install_output_path_count=3" in result.stdout
    assert "guided_install_output_under_tmp_only=true" in result.stdout
