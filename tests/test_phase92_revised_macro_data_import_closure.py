from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase92_revised_macro_data_import_closure import (
    summarize_phase92_revised_macro_data_import_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase92_revised_macro_data_import_closure_passes() -> None:
    summary = summarize_phase92_revised_macro_data_import_closure()

    assert summary["result"] == "passed"
    assert summary["phase92_closure_ready"] is True
    assert summary["revised_macro_data_import_contract_ready"] is True
    assert summary["revised_macro_data_import_dry_run_ready"] is True
    assert summary["postgres_macro_warehouse_dependency_ready"] is True
    assert summary["role_count"] == 39
    assert summary["revised_import_ready_role_count"] == 37
    assert summary["revised_import_blocked_role_count"] == 2
    assert summary["unique_series_count"] == 28
    assert summary["series_registry_row_count"] == 28
    assert summary["source_artifact_row_count"] == 28
    assert summary["observation_revised_row_count"] == 112
    assert summary["observation_vintage_row_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert summary["development_next_phase"] == 93


def test_show_phase92_revised_macro_data_import_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase92_revised_macro_data_import_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase92_closure_ready=true" in result.stdout
    assert "revised_macro_data_import_dry_run_ready=true" in result.stdout
    assert "development_next_phase=93" in result.stdout
    assert "result=passed" in result.stdout
