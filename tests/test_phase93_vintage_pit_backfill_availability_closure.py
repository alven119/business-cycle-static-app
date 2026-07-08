from __future__ import annotations

import subprocess
import sys

import pytest

from business_cycle.audits.phase93_vintage_pit_backfill_availability_closure import (
    summarize_phase93_vintage_pit_backfill_availability_closure,
)

pytestmark = pytest.mark.archive_regression


def test_phase93_vintage_pit_backfill_availability_closure_passes() -> None:
    summary = summarize_phase93_vintage_pit_backfill_availability_closure()

    assert summary["result"] == "passed"
    assert summary["phase93_closure_ready"] is True
    assert summary["vintage_pit_backfill_accounting_ready"] is True
    assert summary["phase92_revised_import_dependency_ready"] is True
    assert summary["postgres_macro_warehouse_dependency_ready"] is True
    assert summary["role_count"] == 39
    assert summary["role_with_pit_backfill_plan_count"] == 34
    assert summary["role_blocked_from_pit_backfill_count"] == 5
    assert summary["planned_vintage_request_row_count"] == 24
    assert summary["observation_vintage_row_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert summary["development_next_phase"] == 94


def test_show_phase93_vintage_pit_backfill_availability_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase93_vintage_pit_backfill_availability_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase93_closure_ready=true" in result.stdout
    assert "vintage_pit_backfill_accounting_ready=true" in result.stdout
    assert "development_next_phase=94" in result.stdout
    assert "result=passed" in result.stdout
