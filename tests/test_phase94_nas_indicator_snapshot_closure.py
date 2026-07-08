from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase94_nas_indicator_snapshot_closure import (
    summarize_phase94_nas_indicator_snapshot_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase94_nas_indicator_snapshot_closure_passes() -> None:
    summary = summarize_phase94_nas_indicator_snapshot_closure()

    assert summary["result"] == "passed"
    assert summary["phase94_closure_ready"] is True
    assert summary["nas_indicator_snapshot_materialization_ready"] is True
    assert summary["phase92_revised_import_dependency_ready"] is True
    assert summary["phase93_pit_availability_dependency_ready"] is True
    assert summary["role_snapshot_count"] == 39
    assert summary["role_with_revised_snapshot_count"] == 37
    assert summary["role_with_pit_backfill_plan_count"] == 34
    assert summary["service_view_model_ready"] is True
    assert summary["api_endpoint_contract_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert summary["development_next_phase"] == 95


def test_show_phase94_nas_indicator_snapshot_closure_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_phase94_nas_indicator_snapshot_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase94_closure_ready=true" in result.stdout
    assert "nas_indicator_snapshot_materialization_ready=true" in result.stdout
    assert "development_next_phase=95" in result.stdout
    assert "result=passed" in result.stdout
