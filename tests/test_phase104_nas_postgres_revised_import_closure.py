from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase104_nas_postgres_revised_import_closure import (
    summarize_phase104_nas_postgres_revised_import_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase104_nas_postgres_revised_import_closure_passes() -> None:
    summary = summarize_phase104_nas_postgres_revised_import_closure()

    assert summary["result"] == "passed"
    assert summary["phase104_closure_ready"] is True
    assert summary["nas_postgres_revised_import_rehearsal_ready"] is True
    assert summary["phase103_connectivity_dependency_ready"] is True
    assert summary["planned_import_row_count"] == 168
    assert summary["backup_rehearsal_plan_ready"] is True
    assert summary["postgres_write_attempt_count"] == 0
    assert summary["development_next_phase"] == 105
    assert (
        summary["phase104_closure_status"]
        == "closed_nas_postgres_revised_import_backup_rehearsal_ready_"
        "no_live_db_write"
    )


def test_show_phase104_nas_postgres_revised_import_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase104_nas_postgres_revised_import_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase104_closure_ready=true" in result.stdout
    assert "nas_postgres_revised_import_rehearsal_ready=true" in result.stdout
    assert "planned_import_row_count=168" in result.stdout
    assert (
        "phase104_closure_status=closed_nas_postgres_revised_import_"
        "backup_rehearsal_ready_no_live_db_write"
    ) in result.stdout
