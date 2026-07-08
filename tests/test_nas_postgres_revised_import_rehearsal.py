from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from business_cycle.storage.nas_postgres_revised_import_rehearsal import (
    build_nas_postgres_revised_import_rehearsal,
    summarize_nas_postgres_revised_import_rehearsal,
    write_nas_postgres_revised_import_rehearsal_report,
)

pytestmark = pytest.mark.archive_regression


def test_nas_postgres_revised_import_rehearsal_summary_passes() -> None:
    summary = summarize_nas_postgres_revised_import_rehearsal()

    assert summary["result"] == "passed"
    assert summary["nas_postgres_revised_import_rehearsal_ready"] is True
    assert summary["phase91_postgres_schema_dependency_ready"] is True
    assert summary["phase92_revised_import_dependency_ready"] is True
    assert summary["phase103_connectivity_dependency_ready"] is True
    assert summary["nas_private_ip"] == "192.168.1.116"
    assert summary["planned_import_table_count"] == 3
    assert summary["planned_import_row_count"] == 168
    assert summary["planned_observation_revised_row_count"] == 112
    assert summary["observation_vintage_row_count"] == 0
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_nas_postgres_revised_import_rehearsal_plans_are_non_executing() -> None:
    rehearsal = build_nas_postgres_revised_import_rehearsal()

    assert rehearsal["import_plan_ready"] is True
    assert rehearsal["backup_rehearsal_plan_ready"] is True
    assert rehearsal["restore_verification_plan_ready"] is True
    assert all(
        row["write_allowed_now"] is False
        for row in rehearsal["table_import_plan"]
    )
    assert rehearsal["backup_rehearsal_plan"]["execution_allowed_now"] is False
    assert all(
        row["execution_allowed_now"] is False
        for row in rehearsal["restore_verification_plan"]
    )
    assert "Do not execute from tests" in rehearsal["deterministic_upsert_sql_preview"]
    assert rehearsal["prohibited_output_field_count"] == 0
    assert rehearsal["secret_value_literal_count"] == 0


def test_nas_postgres_revised_import_rehearsal_writes_only_tmp(
    tmp_path: Path,
) -> None:
    result = write_nas_postgres_revised_import_rehearsal_report(tmp_path)

    assert result["result"] == "passed"
    assert result["rehearsal_output_path_count"] == 6
    assert result["rehearsal_output_under_tmp_only"] is True
    assert result["repo_output_written_count"] == 0
    for path in result["written_paths"]:
        assert Path(path).is_file()
        assert str(path).startswith("/tmp/")


def test_nas_postgres_revised_import_rehearsal_rejects_repo_output() -> None:
    with pytest.raises(ValueError, match="/tmp"):
        write_nas_postgres_revised_import_rehearsal_report(
            Path("tmp-phase104-output"),
        )


def test_show_nas_postgres_revised_import_rehearsal_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_nas_postgres_revised_import_rehearsal.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_postgres_revised_import_rehearsal_ready=true" in result.stdout
    assert "planned_import_row_count=168" in result.stdout
    assert "postgres_write_attempt_count=0" in result.stdout
    assert "result=passed" in result.stdout


def test_run_nas_postgres_revised_import_rehearsal_script(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_nas_postgres_revised_import_rehearsal.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "nas_postgres_revised_import_rehearsal_ready=true" in result.stdout
    assert "rehearsal_output_path_count=6" in result.stdout
    assert "rehearsal_output_under_tmp_only=true" in result.stdout
